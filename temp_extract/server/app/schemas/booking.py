from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .common import BaseSchema
from app.models.enums import BookingStatus


class BookingBase(BaseSchema):
    """Base booking schema"""
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    duration_months: int = 1
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    """Booking creation schema"""
    hostel_id: int  # Changed from str to int to match database
    room_id: str
    
    @validator('duration_months')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be greater than 0')
        return v
    
    @validator('check_in_date')
    def validate_check_in_date(cls, v):
        if v < datetime.now():
            raise ValueError('Check-in date cannot be in the past')
        return v
    
    @validator('check_out_date')
    def validate_check_out_date(cls, v, values):
        if v and 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class BookingUpdate(BaseSchema):
    """Booking update schema"""
    booking_status: Optional[BookingStatus] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    duration_months: Optional[int] = None
    bed_number: Optional[str] = None
    special_requests: Optional[str] = None
    admin_notes: Optional[str] = None
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    refund_amount: Optional[float] = None
    documents: Optional[str] = None


class BookingResponse(BookingBase):
    """Booking response schema"""
    id: str
    user_id: str
    hostel_id: int  # Changed from str to int to match database
    room_id: str
    booking_status: BookingStatus
    booking_date: datetime
    monthly_rent: float
    security_deposit: float
    total_amount: float
    advance_paid: float
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    bed_number: Optional[str] = None
    admin_notes: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    refund_amount: float
    documents: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseSchema):
    """Booking list response schema"""
    id: str
    user_id: str
    user_name: str
    user_email: str
    hostel_id: int  # Changed from str to int to match database
    hostel_name: str
    room_id: str
    room_number: str
    booking_status: BookingStatus
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    total_amount: float
    booking_date: datetime


class BookingSearchParams(BaseSchema):
    """Booking search parameters"""
    user_id: Optional[str] = None
    hostel_id: Optional[int]  # Changed from str to int to match database = None
    room_id: Optional[str] = None
    booking_status: Optional[BookingStatus] = None
    check_in_from: Optional[datetime] = None
    check_in_to: Optional[datetime] = None
    booking_from: Optional[datetime] = None
    booking_to: Optional[datetime] = None


class BookingConfirmation(BaseSchema):
    """Booking confirmation schema"""
    booking_id: str
    bed_number: Optional[str] = None
    admin_notes: Optional[str] = None


class BookingCancellation(BaseSchema):
    """Booking cancellation schema"""
    booking_id: str
    cancellation_reason: str
    refund_amount: Optional[float] = None
    
    @validator('cancellation_reason')
    def validate_reason(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Cancellation reason must be at least 5 characters long')
        return v.strip()