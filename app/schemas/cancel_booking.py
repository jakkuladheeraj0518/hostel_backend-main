from pydantic import BaseModel
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    rejected = "rejected"


class CancelBookingResponse(BaseModel):
    message: str
    refund_amount: float
    status: BookingStatus
    booking_id: int
