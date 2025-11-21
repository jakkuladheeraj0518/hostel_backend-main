from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import NoticeType, TargetAudience


class Notice(BaseEntity):
    """Notice model"""
    __tablename__ = "notices"
    
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    notice_title = Column(String(255), nullable=False)
    notice_content = Column(Text, nullable=False)
    notice_type = Column(SQLEnum(NoticeType), nullable=False)
    is_urgent = Column(Boolean, default=False)
    target_audience = Column(SQLEnum(TargetAudience), nullable=False, default=TargetAudience.ALL)
    
    # Visibility and scheduling
    is_active = Column(Boolean, default=True)
    publish_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Targeting
    target_rooms = Column(String(500), nullable=True)  # JSON string of room numbers
    target_floors = Column(String(100), nullable=True)  # JSON string of floor numbers
    target_user_types = Column(String(200), nullable=True)  # JSON string of user types
    
    # Attachments
    attachments = Column(Text, nullable=True)  # JSON string of file URLs
    
    # Author
    created_by = Column(String, nullable=False)  # User ID of creator
    
    # Read tracking
    read_by = Column(Text, nullable=True)  # JSON string of user IDs who read the notice
    
    # Relationships
    hostel = relationship("Hostel", back_populates="notices")
    
    def __repr__(self):
        return f"<Notice(id={self.id}, title={self.notice_title}, type={self.notice_type})>"