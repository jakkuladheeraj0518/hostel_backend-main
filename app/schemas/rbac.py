"""
Role + permission schema
"""
from pydantic import BaseModel
from typing import List, Optional


class RoleAssign(BaseModel):
    user_id: int
    role: str


class RoleUpdate(BaseModel):
    role: str


class PermissionCheck(BaseModel):
    role: str
    permission: str


class RolePermissionsResponse(BaseModel):
    role: str
    permissions: List[str]

