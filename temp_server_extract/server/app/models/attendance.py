from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Date, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntityWithIntId
from .enums import AttendanceStatus


class Attendance(BaseEntityWithIntId):
    """Attendance model - Required for Supervisor Attendance Operations (as per image)"""
    __tablename__ = "attendance"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    attendance_status = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    
    # Time tracking
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    
    # Leave details (if absent)
    leave_type = Column(String(50), nullable=True)  # sick, personal, emergency, etc.
    leave_reason = Column(Text, nullable=True)
    leave_approved_by = Column(String, nullable=True)  # User ID of approver
    leave_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Supervisor tracking
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Supervisor who marked attendance
    
    # Notes and remarks
    notes = Column(Text, nullable=True)
    supervisor_remarks = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="attendance_records")
    hostel = relationship("Hostel", back_populates="attendance_records")
    marker = relationship("User", foreign_keys=[marked_by])
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.attendance_date}, status={self.attendance_status})>"