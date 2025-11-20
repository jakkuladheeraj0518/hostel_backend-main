# app/models/announcement.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class AnnouncementCategory(str, Enum):
    GENERAL = "general"
    URGENT = "urgent"
    EVENTS = "events"
    RULES = "rules"


class AnnouncementStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Announcement(Base):
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True, index=True)
    announcement_title = Column(String, nullable=False)
    announcement_content = Column(String, nullable=False)
    announcement_category = Column(String, default=AnnouncementCategory.GENERAL.value)
    target_audience = Column(String, default="all")
    scheduled_date = Column(DateTime, nullable=True)
    is_emergency = Column(Boolean, default=False)
    status = Column(String, default=AnnouncementStatus.DRAFT.value)
    attachments = Column(JSON, default=list)
    created_by_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved = Column(Boolean, default=False)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    read_by = Column(JSON, default=list)
