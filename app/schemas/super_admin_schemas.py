from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import time, datetime
from enum import Enum

class Visibility(str, Enum):
    public = "public"
    private = "private"

class HostelBase(BaseModel):
    hostel_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    full_address: Optional[str] = None
    hostel_type: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    amenities: Optional[str] = None
    rules: Optional[str] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    total_beds: Optional[int] = None
    current_occupancy: Optional[int] = None
    monthly_revenue: Optional[float] = None
    visibility: Visibility = Field(default=Visibility.public)
    is_featured: bool = False
    location_id: int  # Ensure location_id is required and must be valid

    @field_validator('current_occupancy')
    @classmethod
    def validate_occupancy(cls, v, info):
        if v is not None and info.data.get('total_beds') is not None and v > info.data['total_beds']:
            raise ValueError('current_occupancy cannot exceed total_beds')
        return v

    @field_validator('check_out')
    @classmethod
    def validate_checkout_time(cls, v, info):
        if v is not None and info.data.get('check_in') is not None:
            # Remove strict validation for check_out
            pass
        return v

class HostelCreate(HostelBase): pass

class HostelUpdate(BaseModel):
    hostel_name: Optional[str] = None
    description: Optional[str] = None
    full_address: Optional[str] = None
    hostel_type: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    amenities: Optional[str] = None
    rules: Optional[str] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    total_beds: Optional[int] = None
    current_occupancy: Optional[int] = None
    monthly_revenue: Optional[float] = None
    visibility: Optional[Visibility] = None
    is_featured: Optional[bool] = None
    location_id: Optional[int] = None

class HostelUpsert(HostelBase):
    id: Optional[int] = None

class HostelResponse(HostelBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ActivityItem(BaseModel):
    entity_name: str
    entity_type: str
    action: str
    created_at: datetime

class DashboardSummary(BaseModel):
    total_hostels: int
    active_admins: int
    average_occupancy: float
    complaint_resolution_rate: float

class TopHostelItem(BaseModel):
    rank: int
    hostel_name: str
    city: str
    total_beds: int
    current_occupancy: int
    occupancy_rate: float

class DashboardResponse(BaseModel):
    summary: DashboardSummary
    recent_activities: List[ActivityItem]
    top_hostels: List[TopHostelItem]

class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None
