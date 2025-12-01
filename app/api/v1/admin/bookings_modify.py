from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
 
from app.dependencies import get_db
from app.schemas.booking import BookingUpdate, BookingResponse
from app.services.booking_service import BookingService
 
from app.dependencies import get_db
from app.schemas.booking import BookingResponse
from app.schemas.cancel_booking import CancelBookingResponse   # ✅ NEW IMPORT
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
 
# ✅ Admin get single booking
@router.get("/{booking_id}", response_model=BookingResponse)
def admin_get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking
 
 
# ✅ Admin confirm booking
@router.put("/{booking_id}/confirm", response_model=BookingResponse)
def admin_confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    updated = BookingService.confirm_booking(db, booking_id)
    return updated
 
 
# ✅ Admin cancel booking
@router.put("/{booking_id}/cancel", response_model=CancelBookingResponse)   # ⭐ FIXED
def admin_cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    updated = BookingService.cancel_booking(db, booking_id)
    return updated