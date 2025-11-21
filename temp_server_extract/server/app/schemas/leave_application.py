from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from app.models.enums import LeaveStatus


class LeaveApplicationBase(BaseModel):
    leave_start_date: date
    leave_end_date: date
    leave_reason: str
    leave_type: str
    emergency_contact: str
    destination: Optional[str] = None
    contact_during_leave: Optional[str] = None


class LeaveApplicationCreate(LeaveApplicationBase):
    student_id: int  # Changed to integer
    parent_consent_required: str = "Y"
    medical_certificate: Optional[str] = None
    supporting_documents: Optional[str] = None


class LeaveApplicationUpdate(BaseModel):
    leave_reason: Optional[str] = None
    emergency_contact: Optional[str] = None
    destination: Optional[str] = None
    contact_during_leave: Optional[str] = None
    expected_return_date: Optional[date] = None


class LeaveApplicationResponse(LeaveApplicationBase):
    id: int  # Changed to integer
    student_id: int
    leave_status: LeaveStatus
    applied_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaveApplicationListResponse(BaseModel):
    id: int  # Changed to integer
    student_id: int
    student_name: str
    leave_start_date: date
    leave_end_date: date
    leave_reason: str
    leave_status: LeaveStatus
    leave_type: str
    emergency_contact: str
    created_at: datetime
    duration_days: int
    
    class Config:
        from_attributes = True


class LeaveApprovalRequest(BaseModel):
    approval_notes: Optional[str] = None


class LeaveRejectionRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=10, max_length=500)


class LeaveReturnConfirmation(BaseModel):
    actual_return_date: date
    return_notes: Optional[str] = None
    is_late_return: bool = False
    late_return_reason: Optional[str] = None


class LeaveApplicationSearchParams(BaseModel):
    status: Optional[LeaveStatus] = None
    leave_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    student_id: Optional[int] = None  # Changed to integer
    pending_only: bool = False