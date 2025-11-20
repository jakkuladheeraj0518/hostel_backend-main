from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.beds import BedStatus  # from app.models.beds.py

# BED SCHEMAS

class BedBase(BaseModel):
    hostel_id: Optional[str] = None
    bed_number: str
    room_number: str
    bed_status: BedStatus = BedStatus.AVAILABLE
    monthly_price: Optional[float] = None
    quarterly_price: Optional[float] = None
    annual_price: Optional[float] = None


class BedCreate(BedBase):
    pass


class BedUpdate(BaseModel):
    hostel_id: Optional[str] = None
    bed_number: Optional[str] = None
    room_number: Optional[str] = None
    bed_status: Optional[BedStatus] = None
    monthly_price: Optional[float] = None
    quarterly_price: Optional[float] = None
    annual_price: Optional[float] = None


class BedOut(BedBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
