from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .common import BaseSchema
from app.models.enums import NoticeType, TargetAudience, UserType


class NoticeBase(BaseSchema):
    """Base notice schema"""
    notice_title: str
    notice_content: str
    notice_type: NoticeType
    is_urgent: bool = False
    target_audience: TargetAudience = TargetAudience.ALL
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class NoticeCreate(NoticeBase):
    """Notice creation schema"""
    hostel_id: int  # Changed from str to int to match database
    target_rooms: Optional[List[str]] = None
    target_floors: Optional[List[int]] = None
    target_user_types: Optional[List[UserType]] = None
    attachments: Optional[str] = None
    
    @validator('notice_title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Notice title must be at least 5 characters long')
        return v.strip()
    
    @validator('notice_content')
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Notice content must be at least 10 characters long')
        return v.strip()
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'publish_date' in values and values['publish_date']:
            if v <= values['publish_date']:
                raise ValueError('Expiry date must be after publish date')
        return v


class NoticeUpdate(BaseSchema):
    """Notice update schema"""
    notice_title: Optional[str] = None
    notice_content: Optional[str] = None
    notice_type: Optional[NoticeType] = None
    is_urgent: Optional[bool] = None
    target_audience: Optional[TargetAudience] = None
    is_active: Optional[bool] = None
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    target_rooms: Optional[List[str]] = None
    target_floors: Optional[List[int]] = None
    target_user_types: Optional[List[UserType]] = None
    attachments: Optional[str] = None


class NoticeResponse(NoticeBase):
    """Notice response schema"""
    id: str
    hostel_id: int  # Changed from str to int to match database
    is_active: bool
    target_rooms: Optional[str] = None
    target_floors: Optional[str] = None
    target_user_types: Optional[str] = None
    attachments: Optional[str] = None
    created_by: str
    read_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class NoticeListResponse(BaseSchema):
    """Notice list response schema"""
    id: str
    notice_title: str
    notice_type: NoticeType
    is_urgent: bool
    target_audience: TargetAudience
    is_active: bool
    hostel_id: int  # Changed from str to int to match database
    hostel_name: str
    created_by: str
    created_by_name: str
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    created_at: datetime


class NoticeSearchParams(BaseSchema):
    """Notice search parameters"""
    hostel_id: Optional[int]  # Changed from str to int to match database = None
    notice_type: Optional[NoticeType] = None
    target_audience: Optional[TargetAudience] = None
    is_urgent: Optional[bool] = None
    is_active: Optional[bool] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class NoticeReadRequest(BaseSchema):
    """Notice read tracking request"""
    notice_id: str
    user_id: str