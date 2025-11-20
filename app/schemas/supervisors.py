from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.supervisors import SupervisorRole, Department, AccessLevel

# SUPERVISOR SCHEMAS

class SupervisorBase(BaseModel):
    supervisor_name: Optional[str] = None
    supervisor_email: Optional[EmailStr] = None
    supervisor_phone: Optional[str] = None
    role: Optional[SupervisorRole] = None
    department: Optional[Department] = None
    access_level: Optional[AccessLevel] = None
    permissions: Optional[str] = None
    status: Optional[str] = None
    invitation_status: Optional[str] = None


class SupervisorCreate(SupervisorBase):
    employee_id: str
    supervisor_name: str
    supervisor_email: EmailStr
    supervisor_phone: str
    role: SupervisorRole


class SupervisorUpdate(BaseModel):
    supervisor_name: Optional[str] = None
    supervisor_email: Optional[EmailStr] = None
    supervisor_phone: Optional[str] = None
    role: Optional[SupervisorRole] = None
    department: Optional[Department] = None
    access_level: Optional[AccessLevel] = None
    permissions: Optional[str] = None
    status: Optional[str] = None
    invitation_status: Optional[str] = None


class SupervisorOut(SupervisorBase):
    employee_id: str

    class Config:
        from_attributes = True


# ADMIN OVERRIDE SCHEMAS

class AdminOverrideCreate(BaseModel):
    admin_employee_id: str
    action: str
    target_supervisor_id: Optional[str] = None
    details: Optional[str] = None


class AdminOverrideOut(AdminOverrideCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
