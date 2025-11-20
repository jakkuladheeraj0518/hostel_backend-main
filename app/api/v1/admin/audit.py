"""
View supervisor activity
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse, AuditLogFilter
from app.schemas.audit import AuditLogBase
from fastapi import Body

router = APIRouter()


@router.get("/audit", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    hostel_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    audit_service = AuditService(db)
    
    filters = AuditLogFilter(
        user_id=user_id,
        hostel_id=hostel_id,
        action=action,
        start_date=start_date,
        end_date=end_date
    )
    
    return audit_service.get_audit_logs(
        viewer_role=current_user.role,
        viewer_user_id=current_user.id,
        skip=skip,
        limit=limit,
        filters=filters
    )


@router.get("/audit/user/{user_id}", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
async def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific user"""
    audit_service = AuditService(db)
    return audit_service.get_user_audit_logs(user_id, skip=skip, limit=limit)


@router.get("/audit/users/{user_id}", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
async def get_user_audit_logs_plural(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Alias endpoint with plural users in path"""
    audit_service = AuditService(db)
    return audit_service.get_user_audit_logs(user_id, skip=skip, limit=limit)


@router.get("/audit/target/{target_id}", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
async def get_audit_by_target(
    target_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Search audit logs by target identifier in resource or details"""
    audit_service = AuditService(db)
    return audit_service.get_target_audit_logs(target_id, skip=skip, limit=limit)


@router.post("/audit/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    payload: AuditLogBase = Body(...),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Create an audit log entry (admins/superadmins can post entries)."""
    audit_service = AuditService(db)
    return audit_service.create_audit_log(
        user_id=current_user.id,
        action=payload.action,
        resource=payload.resource,
        hostel_id=payload.hostel_id,
        ip_address=payload.ip_address,
        user_agent=payload.user_agent,
        details=payload.details
    )

