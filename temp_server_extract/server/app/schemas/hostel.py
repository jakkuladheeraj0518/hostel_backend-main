from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .common import BaseSchema


class HostelBase(BaseSchema):
    """Base hostel schema"""
    name: str
    address: str
    city: str
    state: str
    pincode: str
    description: Optional[str] = None
    amenities: Optional[str] = None
    price_per_month: float
    total_rooms: int
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None


class HostelCreate(HostelBase):
    """Hostel creation schema"""
    
    @validator('price_per_month')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @validator('total_rooms')
    def validate_rooms(cls, v):
        if v <= 0:
            raise ValueError('Total rooms must be greater than 0')
        return v


class HostelUpdate(BaseSchema):
    """Hostel update schema"""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[str] = None
    price_per_month: Optional[float] = None
    total_rooms: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    images: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HostelResponse(HostelBase):
    """Hostel response schema"""
    id: str
    available_rooms: int
    rating: float
    total_reviews: int
    is_active: bool
    is_verified: bool
    images: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class HostelListResponse(BaseSchema):
    """Hostel list response schema"""
    id: str
    name: str
    city: str
    state: str
    price_per_month: float
    rating: float
    total_reviews: int
    available_rooms: int
    is_verified: bool
    images: Optional[str] = None


class HostelSearchParams(BaseSchema):
    """Hostel search parameters"""
    city: Optional[str] = None
    state: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    amenities: Optional[List[str]] = None
    verified_only: bool = False