
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.dependencies import get_db
from app.models.waitlist import Waitlist as WaitlistModel
from app.models.rooms import Room
from app.models.booking import Booking, BookingStatus
from app.services.booking_lock_service import BookingLockService
from app.schemas.waitlist import (
    WaitlistCreate,
    WaitlistResponse,
    PromoteResponse,
)

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


def is_room_available_for_range(db: Session, room_id: int, check_in: datetime, check_out: datetime) -> bool:
    conflict = (
        db.query(Booking)
        .filter(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.confirmed.value,
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        .first()
    )
    return conflict is None


# ---------------------------------------------------------
# ADD TO WAITLIST (Admin + Superadmin only)
# ---------------------------------------------------------
@router.post("/", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_waitlist(
    payload: WaitlistCreate,
    db: Session = Depends(get_db),
    current_user = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_WAITLIST)),
):
    exists = (
        db.query(WaitlistModel)
        .filter(
            WaitlistModel.hostel_id == payload.hostel_id,
            WaitlistModel.room_type == payload.room_type,
            WaitlistModel.visitor_id == payload.visitor_id,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Visitor already on waitlist for this room type")

    top = (
        db.query(WaitlistModel)
        .filter(
            WaitlistModel.hostel_id == payload.hostel_id,
            WaitlistModel.room_type == payload.room_type,
        )
        .order_by(WaitlistModel.priority.desc())
        .first()
    )
    next_priority = (top.priority + 1) if top else 1

    wl = WaitlistModel(
        hostel_id=payload.hostel_id,
        room_type=payload.room_type,
        visitor_id=payload.visitor_id,
        priority=next_priority,
        created_at=datetime.utcnow(),
    )

    db.add(wl)
    db.commit()
    db.refresh(wl)
    return wl


# ---------------------------------------------------------
# LIST WAITLIST (Admin + Superadmin)
# ---------------------------------------------------------
@router.get("/", response_model=List[WaitlistResponse])
def list_waitlist(
    hostel_id: Optional[int] = None,
    room_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_WAITLIST)),
):
    q = db.query(WaitlistModel)
    if hostel_id is not None:
        q = q.filter(WaitlistModel.hostel_id == hostel_id)
    if room_type is not None:
        q = q.filter(WaitlistModel.room_type == room_type)

    q = q.order_by(WaitlistModel.priority.asc(), WaitlistModel.created_at.asc())
    return q.all()


# ---------------------------------------------------------
# DELETE FROM WAITLIST (Admin + Superadmin)
# ---------------------------------------------------------
@router.delete("/{waitlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_waitlist(
    waitlist_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_WAITLIST)),
):
    wl = db.query(WaitlistModel).filter(WaitlistModel.id == waitlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    db.delete(wl)
    db.commit()
    return None


# ---------------------------------------------------------
# PROMOTE WAITLIST ENTRY (Admin + Superadmin)
# ---------------------------------------------------------
@router.post("/{waitlist_id}/promote", response_model=PromoteResponse)
def promote_waitlist_entry(
    waitlist_id: int,
    target_room_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_WAITLIST)),
):
    wl = db.query(WaitlistModel).filter(WaitlistModel.id == waitlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")

    if target_room_id:
        candidate_rooms = db.query(Room).filter(Room.id == target_room_id, Room.hostel_id == wl.hostel_id).all()
        if not candidate_rooms:
            raise HTTPException(status_code=404, detail="Target room not found in the same hostel")
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
                Booking.status == BookingStatus.confirmed.value,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .first()
        )
        if conflict:
            reason = "Conflicting booking exists"
            continue

        try:
            new_booking = Booking(
                visitor_id=wl.visitor_id,
                hostel_id=wl.hostel_id,
                room_id=locked_room.id,
                check_in=check_in,
                check_out=check_out,
                amount_paid=0.0,
                status=BookingStatus.confirmed.value,
                created_at=datetime.utcnow(),
            )

            db.add(new_booking)
            locked_room.available_beds -= 1
            db.delete(wl)

            db.commit()
            db.refresh(new_booking)

            promoted = True
            created_booking = new_booking
            reason = "Promoted"
            break

        except Exception as e:
            db.rollback()
            reason = str(e)
            continue

    if not promoted:
        raise HTTPException(status_code=400, detail=f"Could not promote entry: {reason or 'No room available'}")

    return PromoteResponse(
        promoted=True,
        booking_id=created_booking.id,
        room_id=created_booking.room_id,
        hostel_id=created_booking.hostel_id,
        message="Waitlist entry promoted to confirmed booking"
    )
