from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .common import BaseSchema
from app.models.enums import ComplaintCategory, ComplaintStatus, Priority


class ComplaintBase(BaseSchema):
    """Base complaint schema"""
    complaint_title: str
    complaint_description: str
    complaint_category: ComplaintCategory
    priority: Priority = Priority.MEDIUM
    room_number: Optional[str] = None
    location_details: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    """Complaint creation schema"""
    hostel_id: int  # Changed from str to int to match database
    attachments: Optional[str] = None  # JSON string of file URLs
    
    @validator('complaint_title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Complaint title must be at least 5 characters long')
        return v.strip()
    
    @validator('complaint_description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Complaint description must be at least 10 characters long')
        return v.strip()


class ComplaintUpdate(BaseSchema):
    """Complaint update schema"""
    complaint_title: Optional[str] = None
    complaint_description: Optional[str] = None
    complaint_category: Optional[ComplaintCategory] = None
    complaint_status: Optional[ComplaintStatus] = None
    priority: Optional[Priority] = None
    assigned_to: Optional[int] = None  # Changed to integer
    resolution_notes: Optional[str] = None
    resolution_attachments: Optional[str] = None
    user_rating: Optional[str] = None
    user_feedback: Optional[str] = None


class ComplaintResponse(ComplaintBase):
    """Complaint response schema"""
    id: int
    user_id: int  # Changed to integer
    hostel_id: int  # Changed from str to int to match database
    complaint_status: ComplaintStatus
    assigned_to: Optional[int] = None  # Changed to integer
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    attachments: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolution_attachments: Optional[str] = None
    user_rating: Optional[str] = None
    user_feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ComplaintListResponse(BaseSchema):
    """Complaint list response schema"""
    id: int
    complaint_title: str
    complaint_category: ComplaintCategory
    complaint_status: ComplaintStatus
    priority: Priority
    user_id: int  # Changed to integer
    user_name: str
    hostel_id: int  # Changed from str to int to match database
    hostel_name: str
    room_number: Optional[str] = None
    created_at: datetime


class ComplaintSearchParams(BaseSchema):
    """Complaint search parameters"""
    user_id: Optional[int] = None  # Changed to integer
    hostel_id: Optional[int] = None  # Changed from str to int to match database
    complaint_status: Optional[ComplaintStatus] = None
    complaint_category: Optional[ComplaintCategory] = None
    priority: Optional[Priority] = None
    assigned_to: Optional[int] = None  # Changed to integer
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ComplaintAssignment(BaseSchema):
    """Complaint assignment schema"""
    assigned_to: Optional[int] = None  # Changed to integer (optional if role is provided)
    role: Optional[str] = None  # Role name: maintenance, security, housekeeping, warden
    notes: Optional[str] = None
    
    @validator('role', 'assigned_to')
    def validate_assignment(cls, v, values):
        # At least one of assigned_to or role must be provided
        if 'assigned_to' in values and not values.get('assigned_to') and not v:
            raise ValueError('Either assigned_to (user ID) or role must be provided')
        return v


class ComplaintResolution(BaseSchema):
    """Complaint resolution schema"""
    resolution_notes: str
    resolution_attachments: Optional[str] = None
    
    @validator('resolution_notes')
    def validate_resolution(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Resolution notes must be at least 10 characters long')
        return v.strip()