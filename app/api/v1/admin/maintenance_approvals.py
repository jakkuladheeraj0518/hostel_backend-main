"""
Admin Maintenance Approval Workflow
Approval workflow for high-value repairs requiring admin authorization
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.roles import Role
from app.api.deps import role_required
from app.models.maintenance import MaintenanceRequest

router = APIRouter(prefix="/maintenance/approvals", tags=["Admin Maintenance Approvals"])

# Configurable threshold for high-value repairs
HIGH_VALUE_THRESHOLD = 5000.0  # Default threshold in currency units

@router.get("/threshold")
def get_approval_threshold(
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get the current high-value repair threshold"""
    
    return {
        "threshold": HIGH_VALUE_THRESHOLD,
        "currency": "USD",
        "description": "Repairs exceeding this amount require admin approval"
    }

@router.get("/pending")
def get_pending_approvals(
    hostel_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get maintenance requests pending approval (high-value repairs)"""
    
    query = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.approved == False,
        MaintenanceRequest.est_cost >= HIGH_VALUE_THRESHOLD
    )
    
    if hostel_id:
        query = query.filter(MaintenanceRequest.hostel_id == hostel_id)
    
    requests = query.order_by(desc(MaintenanceRequest.created_at)).offset(skip).limit(limit).all()
    
    return {
        "threshold": HIGH_VALUE_THRESHOLD,
        "pending_count": query.count(),
        "requests": [{
            "id": r.id,
            "hostel_id": r.hostel_id,
            "created_by_id": r.created_by_id,
            "category": r.category,
            "priority": r.priority,
            "status": r.status,
            "description": r.description,
            "photo_url": r.photo_url,
            "est_cost": r.est_cost,
            "actual_cost": r.actual_cost,
            "approved": r.approved,
            "assigned_to_id": r.assigned_to_id,
            "scheduled_date": r.scheduled_date,
            "created_at": r.created_at,
            "requires_approval": r.est_cost >= HIGH_VALUE_THRESHOLD
        } for r in requests]
    }

@router.post("/submit")
def submit_for_approval(
    request_id: int = Query(..., description="Maintenance request ID"),
    justification: Optional[str] = Query(None, description="Justification for high-value repair"),
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR))
):
    """Submit a maintenance request for admin approval (supervisor action)"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    if request.est_cost < HIGH_VALUE_THRESHOLD:
        raise HTTPException(400, f"Request cost ${request.est_cost} is below threshold ${HIGH_VALUE_THRESHOLD}")
    
    if request.approved:
        raise HTTPException(400, "Request already approved")
    
    # Mark as pending approval
    request.status = "PENDING_APPROVAL"
    
    db.commit()
    return {
        "ok": True,
        "message": "Request submitted for admin approval",
        "request_id": request_id,
        "est_cost": request.est_cost,
        "threshold": HIGH_VALUE_THRESHOLD,
        "justification": justification
    }

@router.put("/{request_id}/approve")
def approve_high_value_repair(
    request_id: int,
    approval_notes: Optional[str] = Query(None, description="Admin approval notes"),
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Approve a high-value maintenance repair (admin only)"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    if request.approved:
        raise HTTPException(400, "Request already approved")
    
    request.approved = True
    request.status = "APPROVED"
    
    db.commit()
    return {
        "ok": True,
        "message": "High-value repair approved",
        "request_id": request_id,
        "est_cost": request.est_cost,
        "approved_by_id": user.id,
        "approval_notes": approval_notes
    }

@router.put("/{request_id}/reject")
def reject_high_value_repair(
    request_id: int,
    rejection_reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Reject a high-value maintenance repair (admin only)"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    if request.approved:
        raise HTTPException(400, "Cannot reject already approved request")
    
    request.status = "REJECTED"
    request.approved = False
    
    db.commit()
    return {
        "ok": True,
        "message": "High-value repair rejected",
        "request_id": request_id,
        "est_cost": request.est_cost,
        "rejected_by_id": user.id,
        "rejection_reason": rejection_reason
    }

@router.get("/history")
def get_approval_history(
    hostel_id: Optional[int] = None,
    status: Optional[str] = Query(None, description="APPROVED, REJECTED, PENDING_APPROVAL"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get approval history for high-value repairs"""
    
    query = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.est_cost >= HIGH_VALUE_THRESHOLD
    )
    
    if hostel_id:
        query = query.filter(MaintenanceRequest.hostel_id == hostel_id)
    
    if status:
        if status == "APPROVED":
            query = query.filter(MaintenanceRequest.approved == True)
        elif status == "REJECTED":
            query = query.filter(MaintenanceRequest.status == "REJECTED")
        elif status == "PENDING_APPROVAL":
            query = query.filter(
                MaintenanceRequest.approved == False,
                MaintenanceRequest.status == "PENDING_APPROVAL"
            )
    
    requests = query.order_by(desc(MaintenanceRequest.created_at)).offset(skip).limit(limit).all()
    
    return {
        "threshold": HIGH_VALUE_THRESHOLD,
        "total_count": query.count(),
        "requests": [{
            "id": r.id,
            "hostel_id": r.hostel_id,
            "category": r.category,
            "priority": r.priority,
            "status": r.status,
            "description": r.description,
            "est_cost": r.est_cost,
            "actual_cost": r.actual_cost,
            "approved": r.approved,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        } for r in requests]
    }

@router.get("/stats")
def get_approval_stats(
    hostel_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get statistics for approval workflow"""
    
    query = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.est_cost >= HIGH_VALUE_THRESHOLD
    )
    
    if hostel_id:
        query = query.filter(MaintenanceRequest.hostel_id == hostel_id)
    
    total = query.count()
    approved = query.filter(MaintenanceRequest.approved == True).count()
    rejected = query.filter(MaintenanceRequest.status == "REJECTED").count()
    pending = query.filter(
        MaintenanceRequest.approved == False,
        MaintenanceRequest.status == "PENDING_APPROVAL"
    ).count()
    
    # Calculate total estimated cost
    total_est_cost = db.query(
        db.func.sum(MaintenanceRequest.est_cost)
    ).filter(
        MaintenanceRequest.est_cost >= HIGH_VALUE_THRESHOLD
    ).scalar() or 0
    
    approved_cost = db.query(
        db.func.sum(MaintenanceRequest.est_cost)
    ).filter(
        MaintenanceRequest.est_cost >= HIGH_VALUE_THRESHOLD,
        MaintenanceRequest.approved == True
    ).scalar() or 0
    
    return {
        "threshold": HIGH_VALUE_THRESHOLD,
        "total_high_value_requests": total,
        "approved_count": approved,
        "rejected_count": rejected,
        "pending_count": pending,
        "total_estimated_cost": round(total_est_cost, 2),
        "approved_cost": round(approved_cost, 2),
        "approval_rate": round((approved / total * 100) if total > 0 else 0, 2)
    }
