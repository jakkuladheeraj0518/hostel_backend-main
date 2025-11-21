"""
Supervisor approval request endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.permission_service import PermissionService
from app.schemas.approval import ApprovalRequestCreate

router = APIRouter()


@router.post("/approvals/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_approval_request(
    approval_data: ApprovalRequestCreate,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: Session = Depends(get_db)
):
    """Create an approval request for an action requiring approval"""
    permission_service = PermissionService(db)
    
    # Check if action requires approval
    if not permission_service.requires_approval(approval_data.action, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This action does not require approval for your role"
        )
    
    return permission_service.create_approval_request(
        requester_id=current_user.id,
        action=approval_data.action,
        resource_type=approval_data.resource_type,
        resource_id=approval_data.resource_id,
        hostel_id=approval_data.hostel_id or current_user.hostel_id,
        request_details=approval_data.request_details
    )


@router.get("/approvals/my-requests", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_my_approval_requests(
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: Session = Depends(get_db)
):
    """Get approval requests made by current supervisor"""
    from app.repositories.approval_repository import ApprovalRepository
    approval_repo = ApprovalRepository(db)
    approvals = approval_repo.get_pending_by_requester(current_user.id)
    
    return [
        {
            "id": a.id,
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "status": a.status,
            "created_at": a.created_at,
            "approved_at": a.approved_at
        }
        for a in approvals
    ]


@router.get("/approvals/{approval_id}/status", response_model=dict, status_code=status.HTTP_200_OK)
async def check_approval_status(
    approval_id: int,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: Session = Depends(get_db)
):
    """Check status of an approval request"""
    permission_service = PermissionService(db)
    return permission_service.check_approval_status(approval_id)

