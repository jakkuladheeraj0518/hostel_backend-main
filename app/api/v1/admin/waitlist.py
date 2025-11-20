from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_db
from app.core.auth import admin_required    # 🔐 Admin Authentication

from app.models.waitlist import Waitlist
from app.models.rooms import Room
from app.models.booking import Booking, BookingStatus
from app.services.booking_lock_service import BookingLockService

from app.schemas.waitlist import WaitlistResponse, PromoteResponse


router = APIRouter(prefix="/admin/waitlist", tags=["Admin Waitlist"])


# ---------------------------------------------------------
# Admin List Entire Waitlist
# ---------------------------------------------------------
@router.get("/", response_model=list[WaitlistResponse], dependencies=[Depends(admin_required)])
def list_waitlist(hostel_id: int | None = None, room_type: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Waitlist)
    if hostel_id:
        q = q.filter(Waitlist.hostel_id == hostel_id)
    if room_type:
        q = q.filter(Waitlist.room_type == room_type)

    q = q.order_by(Waitlist.priority.asc(), Waitlist.created_at.asc())
    return q.all()


# ---------------------------------------------------------
# Admin Remove From Waitlist
# ---------------------------------------------------------
@router.delete("/{waitlist_id}", status_code=204, dependencies=[Depends(admin_required)])
def remove_from_waitlist(waitlist_id: int, db: Session = Depends(get_db)):
    wl = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not wl:
        raise HTTPException(404, "Waitlist entry not found")

    db.delete(wl)
    db.commit()
    return None


# ---------------------------------------------------------
# Admin Promote Waitlist Entry → Assign Booking
# ---------------------------------------------------------
@router.post("/{waitlist_id}/promote", response_model=PromoteResponse, dependencies=[Depends(admin_required)])
def promote_waitlist_entry(waitlist_id: int, target_room_id: int | None = None, db: Session = Depends(get_db)):

    wl = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not wl:
        raise HTTPException(404, "Waitlist entry not found")

    # Determine target rooms
    if target_room_id:
        candidate_rooms = db.query(Room).filter(Room.id == target_room_id).all()
        if not candidate_rooms:
            raise HTTPException(404, "Target room not found")
    else:
        candidate_rooms = (
            db.query(Room)
            .filter(Room.hostel_id == wl.hostel_id, Room.room_type == wl.room_type)
            .order_by(Room.available_beds.desc())
            .all()
        )

    promoted = False
    created_booking = None
    reason = None

    for room in candidate_rooms:

        locked_room = BookingLockService.lock_room(db, room.id)
        if not locked_room:
            continue

        if locked_room.available_beds <= 0:
            reason = "No available beds"
            continue

        check_in = datetime.utcnow()
        check_out = datetime(check_in.year + 1, check_in.month, check_in.day)

        conflict = (
            db.query(Booking)
            .filter(
                Booking.room_id == locked_room.id,
                Booking.status == BookingStatus.confirmed,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .first()
        )

        if conflict:
            reason = "Conflicting booking exists"
            continue

        try:
            booking = Booking(
                visitor_id=wl.visitor_id,
                hostel_id=wl.hostel_id,
                room_id=locked_room.id,
                check_in=check_in,
                check_out=check_out,
                amount_paid=0.0,
                status=BookingStatus.confirmed,
                created_at=datetime.utcnow(),
            )

            db.add(booking)
            locked_room.available_beds -= 1
            db.delete(wl)

            db.commit()
            db.refresh(booking)

            created_booking = booking
            promoted = True
            reason = "Promoted"
            break

        except Exception as e:
            db.rollback()
            reason = str(e)
            continue

    if not promoted:
        raise HTTPException(400, f"Could not promote: {reason or 'No room available'}")

    return PromoteResponse(
        promoted=True,
        booking_id=created_booking.id,
        room_id=created_booking.room_id,
        hostel_id=created_booking.hostel_id,
        message="Waitlist entry promoted to confirmed booking"
    )
