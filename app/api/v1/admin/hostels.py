"""
Multi-hostel authorization
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.tenant_service import TenantService
from app.schemas.hostel import HostelResponse

router = APIRouter()


@router.get("/hostels", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_user_hostels(
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get hostels user has access to"""
    tenant_service = TenantService(db)
    return tenant_service.get_user_hostels(current_user.id, current_user.role)


@router.post("/hostels/{hostel_id}/assign-admin/{admin_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def assign_admin_to_hostel(
    hostel_id: int,
    admin_id: int,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Assign admin to hostel (Superadmin only)"""
    tenant_service = TenantService(db)
    return tenant_service.assign_admin_to_hostel(admin_id, hostel_id, current_user.role)




