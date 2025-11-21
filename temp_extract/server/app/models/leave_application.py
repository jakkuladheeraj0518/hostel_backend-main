from sqlalchemy import Column, String, ForeignKey, Date, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntityWithIntId
from .enums import LeaveStatus


class LeaveApplication(BaseEntityWithIntId):
    """Leave Application model"""
    __tablename__ = "leave_applications"
    
    # Applicant details (using user_id instead of student_id for consistency)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Integer FK
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)  # Required for hostel-context filtering
    
    # Leave period
    leave_start_date = Column(Date, nullable=False)
    leave_end_date = Column(Date, nullable=False)
    
    # Leave details
    leave_reason = Column(Text, nullable=False)
    leave_status = Column(SQLEnum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    
    # Emergency contact during leave
    emergency_contact = Column(String(20), nullable=False)
    
    # Additional leave details
    leave_type = Column(String(50), nullable=False)  # casual, medical, emergency, home_visit
    destination = Column(String(255), nullable=True)
    contact_during_leave = Column(String(20), nullable=True)
    
    # Approval workflow
    applied_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Integer FK
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Supporting documents
    medical_certificate = Column(String(500), nullable=True)  # File URL
    supporting_documents = Column(Text, nullable=True)  # JSON string of file URLs
    
    # Parent/Guardian consent
    parent_consent_required = Column(String(1), default='Y')  # Y/N
    parent_consent_received = Column(String(1), default='N')  # Y/N
    parent_contact_verified = Column(String(1), default='N')  # Y/N
    
    # Return details
    expected_return_date = Column(Date, nullable=True)
    actual_return_date = Column(Date, nullable=True)
    return_confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    
    # Late return handling
    is_late_return = Column(String(1), default='N')  # Y/N
    late_return_reason = Column(Text, nullable=True)
    late_return_penalty = Column(String(100), nullable=True)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    applicant = relationship("User", foreign_keys=[applied_by])
    approver = relationship("User", foreign_keys=[approved_by])
    return_confirmer = relationship("User", foreign_keys=[return_confirmed_by])
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    
    def __repr__(self):
        return f"<LeaveApplication(id={self.id}, student_id={self.student_id}, status={self.leave_status})>"
    
    @property
    def leave_duration_days(self):
        """Calculate leave duration in days"""
        if self.leave_start_date and self.leave_end_date:
            return (self.leave_end_date - self.leave_start_date).days + 1
        return 0