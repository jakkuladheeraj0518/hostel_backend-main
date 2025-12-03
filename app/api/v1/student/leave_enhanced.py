"""
Enhanced Student Leave Management Routes
Integrated from hemantPawade.zip - provides leave balance tracking and management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.leave import LeaveRequest
from app.schemas.leave_schema import LeaveCreate
from app.api.deps import role_required
from app.core.roles import Role

router = APIRouter(prefix="/student/leave-enhanced", tags=["Student Leave Enhanced"])

@router.get("/balance")
def get_leave_balance(
    db: Session = Depends(get_db), 
    user: User = Depends(role_required(Role.STUDENT))
):
    """Get student's leave balance and usage statistics"""
    # Calculate leave usage for current year
    current_year = datetime.now().year
    
    # Get all approved leave requests for current year
    approved_leaves = db.query(LeaveRequest).filter(
        and_(
            LeaveRequest.student_id == user.id,
            LeaveRequest.status == "APPROVED",
            extract('year', LeaveRequest.start_date) == current_year
        )
    ).all()
    
    # Calculate total used days
    used_days = 0
    for leave in approved_leaves:
        if leave.start_date and leave.end_date:
            delta = leave.end_date - leave.start_date
            used_days += delta.days + 1  # +1 to include both start and end dates
    
    # Standard leave allocation (can be configured per hostel)
    total_annual_leave = 30  # 30 days per year standard
    remaining_days = max(0, total_annual_leave - used_days)
    
    # Get pending requests
    pending_requests = db.query(LeaveRequest).filter(
        and_(
            LeaveRequest.student_id == user.id,
            LeaveRequest.status == "PENDING",
            extract('year', LeaveRequest.start_date) == current_year
        )
    ).count()
    
    return {
        "total_days": total_annual_leave,
        "used_days": used_days,
        "remaining_days": remaining_days,
        "pending_requests": pending_requests,
        "year": current_year
    }

@router.post("/apply")
def apply_leave(
    leave_data: LeaveCreate, 
    hostel_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(role_required(Role.STUDENT))
):
    """Apply for leave"""
    leave_request = LeaveRequest(
        hostel_id=hostel_id,
        student_id=user.id,
        start_date=leave_data.start,
        end_date=leave_data.end,
        reason=leave_data.reason
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return {"id": leave_request.id}

@router.get("/my")
def get_my_leave_requests(
    db: Session = Depends(get_db), 
    user: User = Depends(role_required(Role.STUDENT))
):
    """Get all leave requests for current student"""
    requests = db.query(LeaveRequest).filter(LeaveRequest.student_id == user.id).all()
    return {"requests": [{"id": r.id, "hostel_id": r.hostel_id, "start_date": r.start_date, 
                         "end_date": r.end_date, "reason": r.reason, "status": r.status} for r in requests]}

@router.put("/{request_id}/cancel")
def cancel_leave_request(
    request_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(role_required(Role.STUDENT))
):
    """Cancel a pending leave request"""
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id, LeaveRequest.student_id == user.id).first()
    if not request:
        raise HTTPException(404, "Leave request not found or not owned by you")
    
    if request.status != "PENDING":
        raise HTTPException(400, "Can only cancel pending requests")
    
    request.status = "CANCELLED"
    db.commit()
    return {"ok": True}
