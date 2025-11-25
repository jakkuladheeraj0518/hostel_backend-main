"""
Role management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.rbac_service import RBACService
from app.services.role_service import RoleService
from app.schemas.rbac import RoleAssign, PermissionCheck, RolePermissionsResponse

router = APIRouter()




@router.post("/rbac/check-permission", response_model=dict, status_code=status.HTTP_200_OK)
async def check_permission(
    check_data: PermissionCheck,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Check if role has permission"""
    rbac_service = RBACService(db)
    has_perm = rbac_service.check_permission(check_data)
    return {
        "role": check_data.role,
        "permission": check_data.permission,
        "has_permission": has_perm
    }


@router.get("/rbac/roles", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_all_roles(
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get all available roles"""
    role_service = RoleService(db)
    return role_service.get_all_available_roles()


@router.get("/rbac/role/{role}/permissions", response_model=RolePermissionsResponse, status_code=status.HTTP_200_OK)
async def get_role_permissions(
    role: str,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get all permissions for a role"""
    rbac_service = RBACService(db)
    return rbac_service.get_role_permissions_list(role)

