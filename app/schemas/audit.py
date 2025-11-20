"""
Audit log schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogBase(BaseModel):
    action: str
    resource: str
    hostel_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    hostel_id: Optional[int] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

