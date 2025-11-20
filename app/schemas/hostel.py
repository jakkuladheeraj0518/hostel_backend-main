"""
Hostel-related schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HostelBase(BaseModel):
    name: str
    address: Optional[str] = None
    capacity: Optional[int] = None


class HostelCreate(HostelBase):
    pass


class HostelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class HostelResponse(HostelBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

