from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.dependencies import get_db
from app.models.hostel import Hostel
from app.models.rooms import Room
from app.models.booking import Booking


router = APIRouter(
    prefix="/visitor/calendar",
    tags=["Booking Calendar"]
)


@router.get("/{hostel_id}")
def get_calendar(
    hostel_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Returns complete booking calendar for visual UI:
    - Room wise bookings
    - Date wise availability
    - Pending bookings included
    """

    # Validate hostel
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found")

    # Fetch all rooms
    rooms = db.query(Room).filter(Room.hostel_id == hostel_id).all()

    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found in this hostel")

    # Fetch bookings within date range
    bookings = (
        db.query(Booking)
        .filter(
            Booking.hostel_id == hostel_id,
            Booking.check_in < end_date,
            Booking.check_out > start_date
        )
        .all()
    )

    # Build calendar data
    calendar = {}

    for room in rooms:
        calendar[room.id] = {
            "room_id": room.id,
            "room_type": room.room_type,
            "price": room.price,
            "dates": {}
        }

        current = start_date
        while current <= end_date:
            calendar[room.id]["dates"][current.isoformat()] = {
                "status": "available",
                "booking_id": None
            }
            current += timedelta(days=1)

    # Mark booked dates
    for b in bookings:
        current = b.check_in.date()
        while current < b.check_out.date():
            if current.isoformat() in calendar[b.room_id]["dates"]:
                calendar[b.room_id]["dates"][current.isoformat()] = {
                    "status": b.status.value,
                    "booking_id": b.id
                }
            current += timedelta(days=1)

    return {
        "hostel_id": hostel.id,
        "hostel_name": hostel.name,
        "start_date": start_date,
        "end_date": end_date,
        "rooms": list(calendar.values())
    }
