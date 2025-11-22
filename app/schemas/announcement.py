# app/schemas/announcement.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.announcement import AnnouncementCategory, AnnouncementStatus

class AnnouncementCreate(BaseModel):
    announcement_title: str
    announcement_content: str
    announcement_category: Optional[AnnouncementCategory] = AnnouncementCategory.GENERAL
    target_audience: Optional[str] = "all"
    scheduled_date: Optional[datetime] = None
    is_emergency: Optional[bool] = False
    attachments: Optional[List[str]] = []

class AnnouncementRead(BaseModel):
    id: int
    announcement_title: str
    announcement_content: str
    announcement_category: AnnouncementCategory
    target_audience: Optional[str]
    scheduled_date: Optional[datetime]
    is_emergency: bool
    status: AnnouncementStatus
    attachments: List[str]
    created_by_id: Optional[int]
    created_at: datetime
    approved: bool

    class Config:
        from_attributes = True

class AnnouncementUpdate(BaseModel):
    announcement_title: Optional[str] = None
    announcement_content: Optional[str] = None
    announcement_category: Optional[AnnouncementCategory] = None
    target_audience: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    is_emergency: Optional[bool] = None
    attachments: Optional[List[str]] = None
    status: Optional[AnnouncementStatus] = None
