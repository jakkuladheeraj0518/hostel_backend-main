"""
Approval request schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.approval_request import ApprovalStatus


class ApprovalRequestBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    hostel_id: Optional[int] = None
    request_details: Optional[str] = None
    threshold_level: int = 1


class ApprovalRequestCreate(ApprovalRequestBase):
    pass


class ApprovalRequestUpdate(BaseModel):
    status: Optional[str] = None
    approval_notes: Optional[str] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    id: int
    requester_id: int
    approver_id: Optional[int] = None
    status: str
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    """Action requiring approval"""
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    threshold_level: int = 1  # Minimum role level required to approve

