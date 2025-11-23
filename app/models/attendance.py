"""
Attendance model for tracking student attendance
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
 
from app.core.database import Base
 
 
class AttendanceStatus(str, enum.Enum):
    """Attendance status enum"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
 
 
class Attendance(Base):
    """Attendance model for student attendance tracking"""
    __tablename__ = "attendance"
   
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    attendance_status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
   
    # Time tracking
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
   
    # Leave details (if absent)
    leave_type = Column(String(50), nullable=True)
    leave_reason = Column(Text, nullable=True)
    leave_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    leave_approved_at = Column(DateTime(timezone=True), nullable=True)
   
    # Supervisor tracking
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
   
    # Notes and remarks
    notes = Column(Text, nullable=True)
    supervisor_remarks = Column(Text, nullable=True)
   
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   
    def __repr__(self):
        return f"<Attendance(id={self.id}, user_id={self.user_id}, date={self.attendance_date}, status={self.attendance_status})>"
 