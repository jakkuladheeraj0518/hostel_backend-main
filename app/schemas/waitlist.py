from pydantic import BaseModel
from datetime import datetime


class WaitlistCreate(BaseModel):
    hostel_id: int
    room_type: str
    visitor_id: int


class WaitlistResponse(BaseModel):
    id: int
    hostel_id: int
    room_type: str
    visitor_id: int
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True


class PromoteResponse(BaseModel):
    promoted: bool
    booking_id: int
    room_id: int
    hostel_id: int
    message: str
