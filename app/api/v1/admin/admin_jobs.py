from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.waitlist_service import WaitlistService

router = APIRouter(prefix="/admin/jobs", tags=["Admin Jobs"])


@router.post("/promote")
def run_waitlist_promotion(
    hostel_id: int,
    room_type: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Manually trigger waitlist promotion.
    """
    booking, entry = WaitlistService.try_promote(db, hostel_id, room_type)

    if booking is None and entry is None:
        return {"message": "No waitlist entries found"}

    if booking:
        return {
            "message": "Promotion successful",
            "booking_id": booking.id,
            "room_id": booking.room_id,
            "visitor_id": booking.visitor_id
        }

    return {"message": "Entry exists but no room currently available"}
