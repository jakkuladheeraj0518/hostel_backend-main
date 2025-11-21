"""
Supervisor Leave Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.leave import LeaveRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/leave-applications", tags=["Supervisor Leave Management"])


@router.get("/")
async def get_leave_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    pending_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get leave applications for supervisor's hostel
    """
    
    query = db.query(LeaveRequest).join(User, LeaveRequest.student_id == User.id)
    
    # Filter by hostel
    if current_user.hostel_id:
        query = query.filter(LeaveRequest.hostel_id == current_user.hostel_id)
    
    # Apply filters
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter.upper())
    
    if pending_only:
        query = query.filter(LeaveRequest.status == "PENDING")
    
    # Order by created date descending
    query = query.order_by(LeaveRequest.id.desc())
    
    total = query.count()
    leave_applications = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    leave_responses = []
    for leave_app in leave_applications:
        student = db.query(User).filter(User.id == leave_app.student_id).first()
        
        # Calculate duration
        duration_days = (leave_app.end_date - leave_app.start_date).days + 1
        
        leave_responses.append({
            "id": leave_app.id,
            "student_id": leave_app.student_id,
            "student_name": student.full_name or student.username if student else "Unknown",
            "leave_start_date": leave_app.start_date.isoformat(),
            "leave_end_date": leave_app.end_date.isoformat(),
            "leave_reason": leave_app.reason,
            "leave_status": leave_app.status.lower(),
            "duration_days": duration_days
        })
    
    total_pages = (total + size - 1) // size
    
    return {
        "items": leave_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }



@router.put("/{leave_id}/approve")
async def approve_leave_application(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve leave application
    """
    
    leave_app = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if student belongs to supervisor's hostel
    if current_user.hostel_id and leave_app.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if leave_app.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave application is not in pending status"
        )
    
    leave_app.status = "APPROVED"
    
    db.commit()
    db.refresh(leave_app)
    
    return {
        "message": "Leave application approved successfully",
        "success": True
    }


@router.put("/{leave_id}/reject")
async def reject_leave_application(
    leave_id: int,
    rejection_reason: str = Query(..., min_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject leave application with reason
    """
    
    leave_app = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if student belongs to supervisor's hostel
    if current_user.hostel_id and leave_app.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if leave_app.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave application is not in pending status"
        )
    
    leave_app.status = "REJECTED"
    # Note: Add rejection_reason field to LeaveRequest model if needed
    
    db.commit()
    db.refresh(leave_app)
    
    return {
        "message": "Leave application rejected successfully",
        "success": True
    }


@router.get("/{leave_id}")
async def get_leave_application(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific leave application details
    """
    
    leave_app = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check access
    if current_user.hostel_id and leave_app.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    student = db.query(User).filter(User.id == leave_app.student_id).first()
    duration_days = (leave_app.end_date - leave_app.start_date).days + 1
    
    return {
        "id": leave_app.id,
        "student_id": leave_app.student_id,
        "student_name": student.full_name or student.username if student else "Unknown",
        "leave_start_date": leave_app.start_date.isoformat(),
        "leave_end_date": leave_app.end_date.isoformat(),
        "leave_reason": leave_app.reason,
        "leave_status": leave_app.status.lower(),
        "duration_days": duration_days,
        "hostel_id": leave_app.hostel_id
    }
