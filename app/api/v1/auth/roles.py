"""
Superadmin role assignment
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.rbac_service import RBACService
from app.schemas.rbac import RoleAssign

router = APIRouter()


@router.post("/assign-role", response_model=dict, status_code=status.HTTP_200_OK)
async def assign_role(
    assign_data: RoleAssign,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Assign role to user (Superadmin only)"""
    rbac_service = RBACService(db)
    return rbac_service.assign_role(assign_data, current_user.role)

