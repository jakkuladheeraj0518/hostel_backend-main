from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.rooms import Room
from app.services.booking_service import BookingService   # ⭐ REQUIRED IMPORT
from app.schemas.booking import BookingUpdate

router = APIRouter(prefix="/calendar", tags=["Calendar"])


# ---------------------------------------------------------
# Helper: Date Range Generator
# ---------------------------------------------------------
def generate_date_range(start: date, end: date):
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days)]


# ---------------------------------------------------------
# 1. CALENDAR FOR A SINGLE ROOM
# ---------------------------------------------------------
@router.get("/room/{room_id}")
def room_calendar(room_id: int, db: Session = Depends(get_db)):

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    bookings = (
        db.query(Booking)
        .filter(Booking.room_id == room_id)
        .all()
    )

    booked_dates = []
    pending_dates = []

    for b in bookings:
        days = generate_date_range(b.check_in.date(), b.check_out.date())

        if b.status == BookingStatus.confirmed.value:
            booked_dates.extend(days)
        elif b.status == BookingStatus.pending.value:
            pending_dates.extend(days)

    return {
        "room_id": room.id,
        "hostel_id": room.hostel_id,
        "room_type": room.room_type,
        "booked_dates": booked_dates,
        "pending_dates": pending_dates,
        "available_beds": room.available_beds,
        "total_beds": room.total_beds,
    }


# ---------------------------------------------------------
# 2. CALENDAR FOR ENTIRE HOSTEL
# ---------------------------------------------------------
@router.get("/hostel/{hostel_id}")
def hostel_calendar(hostel_id: int, db: Session = Depends(get_db)):

    rooms = db.query(Room).filter(Room.hostel_id == hostel_id).all()
    if not rooms:
        raise HTTPException(404, "No rooms found for this hostel")

    hostel_calendar_data = []

    for room in rooms:
        bookings = (
            db.query(Booking)
            .filter(Booking.room_id == room.id)
            .all()
        )

        booked_dates = []
        pending_dates = []

        for b in bookings:
            days = generate_date_range(b.check_in.date(), b.check_out.date())

            if b.status == BookingStatus.confirmed.value:
                booked_dates.extend(days)
            elif b.status == BookingStatus.pending.value:
                pending_dates.extend(days)

        hostel_calendar_data.append({
            "room_id": room.id,
            "room_type": room.room_type,
            "booked_dates": booked_dates,
            "pending_dates": pending_dates,
            "available_beds": room.available_beds,
            "total_beds": room.total_beds,
        })

    return {
        "hostel_id": hostel_id,
        "rooms": hostel_calendar_data
    }


# ---------------------------------------------------------
# 3. DRAG & DROP CHECK → Can move booking?
# ---------------------------------------------------------
@router.get("/drag-drop/validate")
def validate_drag_drop(
    booking_id: int,
    new_room_id: int,
    new_check_in: date,
    new_check_out: date,
    db: Session = Depends(get_db)
):

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")

    # Check room exists
    room = db.query(Room).filter(Room.id == new_room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    # Conflict detection
    conflict = (
        db.query(Booking)
        .filter(
            Booking.room_id == new_room_id,
            Booking.status == BookingStatus.confirmed.value,
            Booking.id != booking_id,
            Booking.check_in < new_check_out,
            Booking.check_out > new_check_in
        )
        .first()
    )

    if conflict:
        return {
            "can_move": False,
            "reason": "Room already booked on selected dates"
        }

    return {"can_move": True}


# ---------------------------------------------------------
# ⭐ NEW → 4. APPLY DRAG & DROP CHANGE (ADMIN)
# ---------------------------------------------------------
@router.post("/drag-drop/apply")
def apply_drag_drop(
    booking_id: int,
    new_room_id: int,
    new_check_in: date,
    new_check_out: date,
    db: Session = Depends(get_db)
):
    """
    Applies actual calendar drag-drop:
    - Moves booking to new room
    - Updates start/end dates
    - Race-safe with row-level locking
    - Uses BookingService.admin_modify_booking()
    """

    updates = BookingUpdate(
        room_id=new_room_id,
        check_in=new_check_in,
        check_out=new_check_out,
    )

    updated = BookingService.admin_modify_booking(db=db, booking_id=booking_id, updates=updates)

    return {
        "message": "Booking updated successfully",
        "booking_id": updated.id,
        "new_room_id": updated.room_id,
        "new_check_in": updated.check_in,
        "new_check_out": updated.check_out
    }
