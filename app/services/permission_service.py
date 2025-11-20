"""
Supervisor permission engine
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime

from app.core.permissions import Permission, has_permission
from app.core.roles import get_role_level
from app.repositories.permission_repository import PermissionRepository
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.permission import PermissionCreate, RolePermissionAssign
from app.schemas.approval import ApprovalRequestCreate, ApprovalAction


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_repo = PermissionRepository(db)
        self.approval_repo = ApprovalRepository(db)
    
    # Approval thresholds for different actions
    APPROVAL_THRESHOLDS = {
        "delete_user": 4,  # Requires Admin level (4) or higher
        "update_user": 3,  # Requires Supervisor level (3) or higher
        "delete_hostel": 5,  # Requires SuperAdmin level (5)
        "create_hostel": 5,  # Requires SuperAdmin level (5)
    }
    
    def check_permission(self, role: str, permission_name: str) -> bool:
        """Check if role has permission (with hierarchical override)"""
        # Check direct permission
        if has_permission(role, permission_name):
            return True
        
        # Check database permissions (for dynamic permissions)
        permissions = self.permission_repo.get_role_permissions(role)
        permission_names = [p.name for p in permissions]
        return permission_name in permission_names
    
    def assign_permission_to_role(self, assign_data: RolePermissionAssign) -> dict:
        """Assign permission to role"""
        # Verify permission exists
        permission = self.permission_repo.get_by_id(assign_data.permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Assign
        role_perm = self.permission_repo.assign_permission_to_role(
            assign_data.role,
            assign_data.permission_id
        )
        
        return {
            "role": role_perm.role,
            "permission_id": role_perm.permission_id,
            "message": "Permission assigned successfully"
        }
    
    def get_role_permissions(self, role: str) -> dict:
        """Get all permissions for a role (static + dynamic)"""
        # Get static permissions
        from app.core.permissions import PERMISSION_MATRIX
        static_perms = list(PERMISSION_MATRIX.get(role, set()))
        
        # Get dynamic permissions from database
        db_permissions = self.permission_repo.get_role_permissions(role)
        dynamic_perms = [p.name for p in db_permissions]
        
        # Combine
        all_permissions = list(set(static_perms + dynamic_perms))
        
        return {
            "role": role,
            "permissions": all_permissions,
            "count": len(all_permissions)
        }
    
    def get_all_permissions(self) -> List[dict]:
        """Get all available permissions"""
        permissions = self.permission_repo.get_all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "resource": p.resource,
                "action": p.action
            }
            for p in permissions
        ]
    
    def requires_approval(self, action: str, user_role: str) -> bool:
        """Check if action requires approval based on threshold"""
        if action not in self.APPROVAL_THRESHOLDS:
            return False
        
        threshold_level = self.APPROVAL_THRESHOLDS[action]
        user_level = get_role_level(user_role)
        
        # If user level is below threshold, approval is required
        return user_level < threshold_level
    
    def create_approval_request(
        self,
        requester_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        hostel_id: Optional[int] = None,
        request_details: Optional[str] = None
    ) -> dict:
        """Create an approval request for an action"""
        threshold_level = self.APPROVAL_THRESHOLDS.get(action, 5)  # Default to SuperAdmin level
        
        approval_data = ApprovalRequestCreate(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            hostel_id=hostel_id,
            request_details=request_details,
            threshold_level=threshold_level
        )
        
        approval_request = self.approval_repo.create(requester_id, approval_data)
        
        return {
            "id": approval_request.id,
            "status": approval_request.status,
            "message": "Approval request created. Waiting for approval.",
            "threshold_level": threshold_level
        }
    
    def check_approval_status(self, approval_id: int) -> dict:
        """Check status of an approval request"""
        approval = self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval request not found"
            )
        
        return {
            "id": approval.id,
            "status": approval.status,
            "action": approval.action,
            "resource_type": approval.resource_type,
            "resource_id": approval.resource_id,
            "created_at": approval.created_at,
            "approved_at": approval.approved_at,
            "approval_notes": approval.approval_notes
        }
    
    def approve_request(self, approval_id: int, approver_id: int, notes: Optional[str] = None) -> dict:
        """Approve an approval request"""
        approval = self.approval_repo.approve(approval_id, approver_id, notes)
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot approve this request. It may not be pending or not found."
            )
        
        return {
            "id": approval.id,
            "status": approval.status,
            "message": "Request approved successfully"
        }
    
    def reject_request(self, approval_id: int, approver_id: int, notes: Optional[str] = None) -> dict:
        """Reject an approval request"""
        approval = self.approval_repo.reject(approval_id, approver_id, notes)
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reject this request. It may not be pending or not found."
            )
        
        return {
            "id": approval.id,
            "status": approval.status,
            "message": "Request rejected"
        }
    
    def get_pending_approvals(self, approver_role: str, hostel_id: Optional[int] = None) -> List[dict]:
        """Get pending approvals that approver can handle"""
        approver_level = get_role_level(approver_role)
        approvals = self.approval_repo.get_pending_for_approver(approver_level, hostel_id)
        
        return [
            {
                "id": a.id,
                "requester_id": a.requester_id,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "hostel_id": a.hostel_id,
                "request_details": a.request_details,
                "threshold_level": a.threshold_level,
                "created_at": a.created_at
            }
            for a in approvals
        ]

