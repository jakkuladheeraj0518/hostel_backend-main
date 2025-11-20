"""
Get current user information endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.tenant_service import TenantService
from app.core.permissions import get_role_permissions, PERMISSION_MATRIX

router = APIRouter()


@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK, tags=["auth"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current logged-in user information
    
    Returns the user's profile information based on the JWT token.
    Useful for checking who is logged in, especially when multiple tabs are open.
    
    Requires: Authorization header with Bearer token
    """
    # Get user's accessible hostels if admin
    accessible_hostels = []
    if current_user.role in ["admin", "superadmin"]:
        tenant_service = TenantService(db)
        accessible_hostels = tenant_service.get_user_hostels(current_user.id, current_user.role)
    
    # Get hostel name if hostel_id exists
    hostel_name = None
    if current_user.hostel_id:
        from app.repositories.hostel_repository import HostelRepository
        hostel_repo = HostelRepository(db)
        hostel = hostel_repo.get_by_id(current_user.hostel_id)
        if hostel:
            hostel_name = hostel.name
    
    # compute permissions info for the current role
    role_permissions = set(get_role_permissions(current_user.role))
    # gather all known permissions to present a stable map
    all_permissions = set()
    for perms in PERMISSION_MATRIX.values():
        all_permissions.update(perms)

    permissions_map = {p: (p in role_permissions) for p in sorted(all_permissions)}

    return {
        "id": current_user.id,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "country_code": current_user.country_code,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "permissions": sorted(role_permissions),
        "permissions_map": permissions_map,
        "hostel_id": current_user.hostel_id,
        "hostel_name": hostel_name,
        "is_active": current_user.is_active,
        "is_email_verified": getattr(current_user, "is_email_verified", False),
        "is_phone_verified": getattr(current_user, "is_phone_verified", False),
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "accessible_hostels": accessible_hostels if accessible_hostels else None,
        "remember_me": getattr(current_user, "remember_me", False)
    }


