from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum

class PermissionLevel(str, Enum):
    read = "read"
    write = "write"
    admin = "admin"

class AdminBase(BaseModel):
    admin_name: str
    email: EmailStr
    is_active: bool = True

class AdminCreate(AdminBase):
    pass

class AdminResponse(AdminBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True

class AdminHostelAssignmentBase(BaseModel):
    permission_level: PermissionLevel = PermissionLevel.read

class AdminHostelAssignmentCreate(AdminHostelAssignmentBase):
    hostel_id: int

class AdminHostelAssignmentResponse(AdminHostelAssignmentBase):
    id: int
    admin_id: int
    hostel_id: int
    assigned_at: datetime

    class Config:
        from_attributes = True

class BulkAssignmentRequest(BaseModel):
    admin_id: int
    hostel_ids: List[int]
    permission_level: PermissionLevel = PermissionLevel.read

class BulkAssignmentResponse(BaseModel):
    success: bool
    message: str
    assignments: List[AdminHostelAssignmentResponse]