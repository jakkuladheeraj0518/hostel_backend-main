from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntityWithIntId
from .enums import ComplaintCategory, ComplaintStatus, Priority


class Complaint(BaseEntityWithIntId):
    """Complaint model with integer ID (1, 2, 3...)"""
    __tablename__ = "complaints"
    
    # Override to ensure integer ID behavior
    __mapper_args__ = {
        'polymorphic_identity': 'complaint'
    }
    
    # Complaint details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    complaint_title = Column(String(255), nullable=False)
    complaint_description = Column(Text, nullable=False)
    complaint_category = Column(SQLEnum(ComplaintCategory), nullable=False)
    complaint_status = Column(SQLEnum(ComplaintStatus), nullable=False, default=ComplaintStatus.OPEN)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    
    # Assignment and resolution
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional details
    room_number = Column(String(50), nullable=True)
    location_details = Column(String(500), nullable=True)
    attachments = Column(Text, nullable=True)  # JSON string of file URLs
    
    # Resolution details
    resolution_notes = Column(Text, nullable=True)
    resolution_attachments = Column(Text, nullable=True)
    user_rating = Column(String(10), nullable=True)
    user_feedback = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="complaints")
    hostel = relationship("Hostel", back_populates="complaints")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    
    def __repr__(self):
        return f"<Complaint(id={self.id}, title={self.complaint_title}, status={self.complaint_status})>"