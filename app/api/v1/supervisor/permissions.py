"""
Manage Supervisor & Admin permission rules
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required
from app.models.user import User
from app.services.permission_service import PermissionService
from app.schemas.permission import RolePermissionAssign

router = APIRouter()


# ---------------------------
# Assign Permission to Role
# ---------------------------
@router.post("/permissions/assign", response_model=dict, status_code=status.HTTP_200_OK)
async def assign_permission_to_role(
    assign_data: RolePermissionAssign,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Assign permission to role (Superadmin only)"""
    return PermissionService(db).assign_permission_to_role(assign_data)


# ---------------------------
# Get permissions for a role
# ---------------------------
@router.get("/permissions/role/{role}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_role_permissions(
    role: str,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Return all permissions for a role"""
    return PermissionService(db).get_role_permissions(role)


# ---------------------------
# Get all permissions
# ---------------------------
@router.get("/permissions/all", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_all_permissions(
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Return all available permissions"""
    return PermissionService(db).get_all_permissions()
