from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .common import BaseSchema
from app.models.enums import RoomType


class RoomBase(BaseSchema):
    """Base room schema"""
    room_number: str
    room_type: RoomType
    capacity: int
    price_per_month: float
    floor_number: Optional[int] = None
    area_sqft: Optional[float] = None
    has_attached_bathroom: bool = False
    has_balcony: bool = False
    has_ac: bool = False
    has_wifi: bool = True


class RoomCreate(RoomBase):
    """Room creation schema"""
    hostel_id: int  # Changed from str to int to match database
    
    @validator('capacity')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v
    
    @validator('price_per_month')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class RoomUpdate(BaseSchema):
    """Room update schema"""
    room_number: Optional[str] = None
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = None
    price_per_month: Optional[float] = None
    floor_number: Optional[int] = None
    area_sqft: Optional[float] = None
    has_attached_bathroom: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_ac: Optional[bool] = None
    has_wifi: Optional[bool] = None
    is_under_maintenance: Optional[bool] = None
    maintenance_notes: Optional[str] = None
    images: Optional[str] = None


class RoomResponse(RoomBase):
    """Room response schema"""
    id: str
    hostel_id: int  # Changed from str to int to match database
    current_occupancy: int
    is_occupied: bool
    is_under_maintenance: bool
    maintenance_notes: Optional[str] = None
    images: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @property
    def is_available(self) -> bool:
        return self.current_occupancy < self.capacity and not self.is_under_maintenance


class RoomListResponse(BaseSchema):
    """Room list response schema"""
    id: str
    room_number: str
    room_type: RoomType
    capacity: int
    current_occupancy: int
    price_per_month: float
    is_available: bool
    is_under_maintenance: bool


class RoomSearchParams(BaseSchema):
    """Room search parameters"""
    room_type: Optional[RoomType] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available_only: bool = True
    has_ac: Optional[bool] = None
    has_attached_bathroom: Optional[bool] = None
    floor_number: Optional[int] = None