"""
Permission schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RolePermissionAssign(BaseModel):
    role: str
    permission_id: int

