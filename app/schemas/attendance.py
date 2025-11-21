"""
Attendance schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    """Attendance status enum"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AttendanceCreate(BaseModel):
    """Schema for creating attendance record"""
    user_id: int
    hostel_id: int
    attendance_date: date
    attendance_status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    leave_type: Optional[str] = None
    leave_reason: Optional[str] = None
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance record"""
    attendance_status: Optional[AttendanceStatus] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    leave_type: Optional[str] = None
    leave_reason: Optional[str] = None
    notes: Optional[str] = None
    supervisor_remarks: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Schema for attendance response"""
    id: int
    user_id: int
    hostel_id: int
    attendance_date: date
    attendance_status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    leave_type: Optional[str] = None
    leave_reason: Optional[str] = None
    leave_approved_by: Optional[int] = None
    leave_approved_at: Optional[datetime] = None
    marked_by: Optional[int] = None
    notes: Optional[str] = None
    supervisor_remarks: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    """Schema for attendance list item"""
    user_id: int
    user_name: str
    id: int
    attendance_date: date
    attendance_status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceSearchParams(BaseModel):
    """Schema for attendance search parameters"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    user_id: Optional[int] = None
    status: Optional[AttendanceStatus] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class QuickMarkAttendance(BaseModel):
    """Schema for quick attendance marking"""
    attendance_status: AttendanceStatus
