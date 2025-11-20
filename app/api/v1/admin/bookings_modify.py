from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.booking import BookingUpdate, BookingResponse
from app.services.booking_service import BookingService


router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin Booking Modification"]
)


@router.put("/{booking_id}/modify", response_model=BookingResponse)
def admin_modify_booking(
    booking_id: int,
    updates: BookingUpdate,
    db: Session = Depends(get_db)
):
    """
    Admin-level booking modification:
    - Change room
    - Change dates
    - Change both
    - Checks for overlap automatically
    """
    updated = BookingService.modify_booking(db, booking_id, updates)
    return updated
