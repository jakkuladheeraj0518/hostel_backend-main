"""
Dependency functions (get_current_user, role_required)
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.roles import Role
from app.core.permissions import has_permission
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.core.database import get_db


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """Get database session"""
    return db


def get_active_hostel_id(request: Request) -> Optional[int]:
    """Get active hostel_id from request state (set by TenantFilterMiddleware)"""
    if hasattr(request.state, "bypass_tenant_filter") and request.state.bypass_tenant_filter:
        return None  # Superadmin bypass
    return getattr(request.state, "active_hostel_id", None)


def get_user_hostel_ids(user_id: int, user_role: str, db: Session) -> List[int]:
    """Get list of hostel IDs user has access to"""
    from app.repositories.hostel_repository import HostelRepository
    from app.repositories.user_repository import UserRepository
    
    if user_role == Role.SUPERADMIN:
        # Superadmin has access to all hostels
        hostel_repo = HostelRepository(db)
        hostels = hostel_repo.get_all_hostels(skip=0, limit=1000)
        return [h.id for h in hostels]
    elif user_role == Role.ADMIN:
        # Admin has access to assigned hostels
        hostel_repo = HostelRepository(db)
        hostels = hostel_repo.get_by_admin(user_id)
        return [h.id for h in hostels]
    else:
        # Other roles have access to their own hostel
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if user and user.hostel_id:
            return [user.hostel_id]
        return []


def role_required(*allowed_roles: str):
    """Dependency to check if user has required role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AccessDeniedException(
                f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def permission_required(permission: str):
    """Dependency to check if user has required permission"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise AccessDeniedException(
                f"Access denied. Required permission: {permission}"
            )
        return current_user
    return permission_checker


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


def get_repository_context(
    current_user: User = Depends(get_current_active_user),
    request: Optional[Request] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Get context for repositories (user role, active hostel, accessible hostels)"""
    active_hostel_id = get_active_hostel_id(request) if request else None
    user_hostel_ids = get_user_hostel_ids(current_user.id, current_user.role, db)
    
    return {
        "user_role": current_user.role,
        "active_hostel_id": active_hostel_id,
        "user_hostel_ids": user_hostel_ids
    }

