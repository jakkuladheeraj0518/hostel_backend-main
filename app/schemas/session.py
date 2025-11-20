"""
Active session (switch hostel) schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionContextBase(BaseModel):
    hostel_id: int


class SessionContextCreate(SessionContextBase):
    pass


class SessionContextResponse(SessionContextBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SwitchSessionRequest(BaseModel):
    hostel_id: int

