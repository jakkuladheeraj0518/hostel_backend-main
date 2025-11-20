"""
Approval request model for supervisor actions requiring approval
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Supervisor requesting
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin/SuperAdmin approving
    action = Column(String, nullable=False)  # e.g., "update_user", "delete_user"
    resource_type = Column(String, nullable=False)  # e.g., "user", "hostel"
    resource_id = Column(Integer, nullable=True)  # ID of the resource being acted upon
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    status = Column(String, default=ApprovalStatus.PENDING.value, nullable=False)
    request_details = Column(Text, nullable=True)  # JSON string with request details
    approval_notes = Column(Text, nullable=True)  # Notes from approver
    threshold_level = Column(Integer, nullable=False, default=1)  # Approval threshold level required
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="approval_requests_made")
    approver = relationship("User", foreign_keys=[approver_id], backref="approval_requests_approved")
    hostel = relationship("Hostel", back_populates="approval_requests")

