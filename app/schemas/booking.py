from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    rejected = "rejected"




class BookingCreate(BaseModel):
    visitor_id: int
    hostel_id: int
    room_id: int
    check_in: datetime
    check_out: datetime
    amount_paid: float = 0   # Required for model

# Add BookingCreateSchema alias for compatibility
class BookingCreateSchema(BookingCreate):
    pass



class BookingUpdate(BaseModel):
    check_in: datetime | None = None
    check_out: datetime | None = None
    room_id: int | None = None

# Add BookingUpdateSchema alias for compatibility
class BookingUpdateSchema(BookingUpdate):
    pass



class BookingStatusUpdate(BaseModel):
    status: BookingStatus

# Add BookingStatusUpdateSchema alias for compatibility
class BookingStatusUpdateSchema(BookingStatusUpdate):
    pass



class BookingResponse(BaseModel):
    id: int
    visitor_id: int
    hostel_id: int
    room_id: int
    check_in: datetime
    check_out: datetime
    status: BookingStatus
    amount_paid: float

    class Config:
        from_attributes = True   # Pydantic v2 replacement for from_attributes

# Add BookingResponseSchema alias for compatibility
class BookingResponseSchema(BookingResponse):
    pass
