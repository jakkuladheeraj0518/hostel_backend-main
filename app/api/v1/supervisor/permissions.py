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


