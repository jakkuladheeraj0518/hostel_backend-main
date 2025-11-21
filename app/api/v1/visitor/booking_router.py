from fastapi import APIRouter, Depends, status, HTTPException, Path, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.booking_schema import BookingCreate, BookingResponse, BookingStatusUpdate
from app.services.booking_service import create_booking, update_booking_status
from app.core.security import get_current_user

router = APIRouter(tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking_request(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # FIX: Use .id (attribute access) because current_user is a User object
    booking = create_booking(db, user_id=current_user.id, booking_data=booking_data)
    return booking


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status_route(
    booking_id: int = Path(..., description="Booking ID to update"),
    update_data: BookingStatusUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    booking = update_booking_status(db, booking_id=booking_id, status=update_data.status)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
