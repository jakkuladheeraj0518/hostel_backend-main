"""
Approval request repository
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.approval_request import ApprovalRequest, ApprovalStatus
from app.schemas.approval import ApprovalRequestCreate, ApprovalRequestUpdate


class ApprovalRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, requester_id: int, approval_data: ApprovalRequestCreate) -> ApprovalRequest:
        """Create new approval request"""
        approval_request = ApprovalRequest(
            requester_id=requester_id,
            action=approval_data.action,
            resource_type=approval_data.resource_type,
            resource_id=approval_data.resource_id,
            hostel_id=approval_data.hostel_id,
            request_details=approval_data.request_details,
            threshold_level=approval_data.threshold_level,
            status=ApprovalStatus.PENDING.value
        )
        self.db.add(approval_request)
        self.db.commit()
        self.db.refresh(approval_request)
        return approval_request
    
    def get_by_id(self, approval_id: int) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        return self.db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    
    def get_pending_by_requester(self, requester_id: int) -> List[ApprovalRequest]:
        """Get pending approval requests for a requester"""
        return self.db.query(ApprovalRequest).filter(
            ApprovalRequest.requester_id == requester_id,
            ApprovalRequest.status == ApprovalStatus.PENDING.value
        ).order_by(ApprovalRequest.created_at.desc()).all()
    
    def get_pending_for_approver(self, approver_role_level: int, hostel_id: Optional[int] = None) -> List[ApprovalRequest]:
        """Get pending approval requests that approver can handle"""
        query = self.db.query(ApprovalRequest).filter(
            ApprovalRequest.status == ApprovalStatus.PENDING.value,
            ApprovalRequest.threshold_level <= approver_role_level
        )
        if hostel_id:
            query = query.filter(ApprovalRequest.hostel_id == hostel_id)
        return query.order_by(ApprovalRequest.created_at.desc()).all()
    
    def approve(self, approval_id: int, approver_id: int, notes: Optional[str] = None) -> Optional[ApprovalRequest]:
        """Approve a request"""
        approval = self.get_by_id(approval_id)
        if not approval or approval.status != ApprovalStatus.PENDING.value:
            return None
        
        from datetime import datetime
        approval.status = ApprovalStatus.APPROVED.value
        approval.approver_id = approver_id
        approval.approval_notes = notes
        approval.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def reject(self, approval_id: int, approver_id: int, notes: Optional[str] = None) -> Optional[ApprovalRequest]:
        """Reject a request"""
        approval = self.get_by_id(approval_id)
        if not approval or approval.status != ApprovalStatus.PENDING.value:
            return None
        
        from datetime import datetime
        approval.status = ApprovalStatus.REJECTED.value
        approval.approver_id = approver_id
        approval.approval_notes = notes
        approval.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(approval)
        return approval

