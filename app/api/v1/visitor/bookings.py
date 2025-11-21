from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/visitor/bookings", tags=["Visitor Bookings"])


# ---------------------------------------------------------
# CREATE BOOKING (Visitor)
# ---------------------------------------------------------
@router.post("/", response_model=BookingResponse)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    """
    Visitor booking creation.
    Double-booking prevention and locking are handled in BookingService.
    """
    return BookingService.create_booking(db, data)


# ---------------------------------------------------------
# MODIFY BOOKING (Visitor)
# ---------------------------------------------------------
@router.put("/{booking_id}", response_model=BookingResponse)
def modify_booking(booking_id: int, updates: BookingUpdate, db: Session = Depends(get_db)):
    return BookingService.modify_booking(db, booking_id, updates)


# ---------------------------------------------------------
# CANCEL BOOKING (Visitor)
# ---------------------------------------------------------
@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    return BookingService.cancel_booking(db, booking_id)


# ---------------------------------------------------------
# GET BOOKING (Visitor)
# ---------------------------------------------------------
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking
