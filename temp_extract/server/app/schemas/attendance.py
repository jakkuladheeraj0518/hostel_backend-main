from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from .common import BaseSchema
from app.models.enums import AttendanceStatus


class AttendanceBase(BaseSchema):
    user_id: int  # Integer ID
    hostel_id: int  # Changed from str to int to match database
    attendance_date: date
    attendance_status: AttendanceStatus = AttendanceStatus.PRESENT
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    leave_type: Optional[str] = None
    leave_reason: Optional[str] = None
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    attendance_status: Optional[AttendanceStatus] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    leave_type: Optional[str] = None
    leave_reason: Optional[str] = None
    notes: Optional[str] = None
    supervisor_remarks: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int  # Integer ID
    marked_by: Optional[int] = None  # Integer ID
    leave_approved_by: Optional[str] = None
    leave_approved_at: Optional[datetime] = None
    supervisor_remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AttendanceListResponse(BaseSchema):
    user_id: int  # User ID first for proper sequence (integer: 1, 2, 3...)
    user_name: str
    id: int  # Attendance ID second (attendance record ID, integer: 1, 2, 3...)
    attendance_date: date
    attendance_status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceSearchParams(BaseSchema):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    user_id: Optional[int] = None  # Integer ID
    status: Optional[AttendanceStatus] = None
    hostel_id: Optional[int] = None  # Changed from str to int to match database