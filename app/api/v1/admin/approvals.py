"""
Approval management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.permission_service import PermissionService
from app.schemas.approval import ApprovalRequestResponse

router = APIRouter()


@router.get("/approvals/pending", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_pending_approvals(
    hostel_id: Optional[int] = Query(None),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get pending approval requests that current user can approve"""
    permission_service = PermissionService(db)
    return permission_service.get_pending_approvals(current_user.role, hostel_id)


@router.post("/approvals/{approval_id}/approve", response_model=dict, status_code=status.HTTP_200_OK)
async def approve_request(
    approval_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Approve an approval request"""
    permission_service = PermissionService(db)
    return permission_service.approve_request(approval_id, current_user.id, notes)


@router.post("/approvals/{approval_id}/reject", response_model=dict, status_code=status.HTTP_200_OK)
async def reject_request(
    approval_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Reject an approval request"""
    permission_service = PermissionService(db)
    return permission_service.reject_request(approval_id, current_user.id, notes)


@router.get("/approvals/{approval_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_approval_status(
    approval_id: int,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR)),
    db: Session = Depends(get_db)
):
    """Get approval request status"""
    permission_service = PermissionService(db)
    return permission_service.check_approval_status(approval_id)

