"""
Manage supervisor permission rules
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.permission_service import PermissionService
from app.schemas.permission import RolePermissionAssign

router = APIRouter()



@router.get("/permissions/role/{role}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_role_permissions(
    role: str,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get all permissions for a role"""
    permission_service = PermissionService(db)
    return permission_service.get_role_permissions(role)


@router.get("/permissions/all", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_all_permissions(
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get all available permissions"""
    permission_service = PermissionService(db)
    return permission_service.get_all_permissions()

