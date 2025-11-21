from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Completed = "Completed"


class BookingCreate(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    id_type: str
    id_number: str
    id_document: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_number: str
    emergency_contact_relation: Optional[str] = None
    special_requirements: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    status: BookingStatus
    created_at: datetime

    class Config:
        orm_mode = True


class BookingStatusUpdate(BaseModel):
    status: BookingStatus

