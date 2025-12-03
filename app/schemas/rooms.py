from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.rooms import RoomType, MaintenanceStatus

# ROOM SCHEMAS

class RoomBase(BaseModel):
    hostel_id: Optional[int] = None
    room_number: str
    room_type: RoomType = RoomType.SINGLE
    room_capacity: int = 1
    monthly_price: Optional[float] = None
    quarterly_price: Optional[float] = None
    annual_price: Optional[float] = None
    availability: int = 0
    amenities: Optional[str] = None
    maintenance_status: MaintenanceStatus = MaintenanceStatus.OK


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    hostel_id: Optional[int] = None
    room_number: Optional[str] = None
    room_type: Optional[RoomType] = None
    room_capacity: Optional[int] = None
    monthly_price: Optional[float] = None
    quarterly_price: Optional[float] = None
    annual_price: Optional[float] = None
    availability: Optional[int] = None
    amenities: Optional[str] = None
    maintenance_status: Optional[MaintenanceStatus] = None


class RoomOut(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
