"""
Supervisor activity logs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
 
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse, AuditLogFilter
from app.schemas.audit import AuditLogBase
from fastapi import Body
 
router = APIRouter()
 
 
@router.get("/audit", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
async def get_supervisor_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    hostel_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    _perm: User = Depends(permission_required(Permission.VIEW_AUDIT)),
    db: Session = Depends(get_db)
):
    """Get audit logs for supervisor"""
    audit_service = AuditService(db)
    # Get supervisor's assigned hostels
    user_hostel_ids = get_user_hostel_ids(current_user.id, current_user.role, db)
    # Allow if supervisor has global access (empty hostel_ids) OR hostel_id is in their assigned list
    if user_hostel_ids and hostel_id and hostel_id not in user_hostel_ids:
        raise AccessDeniedException(
            f"Supervisors can only view logs for their assigned hostel(s). Assigned hostels: {user_hostel_ids}"
        )
 
    filters = AuditLogFilter(
        user_id=current_user.id,
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
 
 
 
@router.post("/audit/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def supervisor_create_audit_log(
    payload: AuditLogBase = Body(...),
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    _perm: User = Depends(permission_required(Permission.CREATE_AUDIT)),
    db: Session = Depends(get_db)
):
    """Create an audit log entry (supervisors can post entries)."""
    # Determine target hostel for the audit log
    target_hostel = payload.hostel_id or current_user.hostel_id
   
    # Get supervisor's assigned hostels
    user_hostel_ids = get_user_hostel_ids(current_user.id, current_user.role, db)
   
    # Allow if:
    # 1. Supervisor has global access (hostel_id is null, so user_hostel_ids is empty)
    # 2. OR target hostel is in their assigned hostels
    if user_hostel_ids and target_hostel and target_hostel not in user_hostel_ids:
        raise AccessDeniedException(
            f"Supervisor cannot create logs for hostels outside their assignment. Assigned hostels: {user_hostel_ids}"
        )
 
    audit_service = AuditService(db)
    return audit_service.create_audit_log(
        user_id=current_user.id,
        action=payload.action,
        resource=payload.resource,
        hostel_id=target_hostel,
        ip_address=payload.ip_address,
        user_agent=payload.user_agent,
        details=payload.details
    )
 