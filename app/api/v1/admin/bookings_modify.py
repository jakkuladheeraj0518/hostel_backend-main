
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.booking import BookingUpdate, BookingResponse
from app.schemas.cancel_booking import CancelBookingResponse
from app.services.booking_service import BookingService

from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required


router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin Booking Modification"]
)


#  Admin MODIFY booking
@router.put("/{booking_id}/modify", response_model=BookingResponse)
def admin_modify_booking(
    booking_id: int,
    updates: BookingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = BookingService.modify_booking(db, booking_id, updates)
    return updated


#  Admin GET single booking
@router.get("/{booking_id}", response_model=BookingResponse)
def admin_get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking


#  Admin CONFIRM booking
@router.put("/{booking_id}/confirm", response_model=BookingResponse)
def admin_confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = BookingService.confirm_booking(db, booking_id)
    return updated


#  Admin CANCEL booking
@router.put("/{booking_id}/cancel", response_model=CancelBookingResponse)
def admin_cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = BookingService.cancel_booking(db, booking_id)
    # Build response matching CancelBookingResponse schema
    return CancelBookingResponse(
        message="Booking cancelled successfully",
        refund_amount=getattr(updated, "refund_amount", 0.0),
        status=updated.status,
        booking_id=updated.id,
    )
