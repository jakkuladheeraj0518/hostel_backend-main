"""
Supervisor Attendance API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List

from app.core.database import get_db
from app.models.user import User
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.attendance import (
    AttendanceResponse,
    AttendanceListResponse,
    AttendanceCreate,
    AttendanceUpdate,
    QuickMarkAttendance
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/attendance", tags=["Supervisor Attendance"])


@router.get("/")
async def get_attendance_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[AttendanceStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get attendance records with filtering and pagination
    """
    
    query = db.query(Attendance)
    
    # Filter by hostel
    if current_user.hostel_id:
        query = query.filter(Attendance.hostel_id == current_user.hostel_id)
    
    # Apply filters
    if date_from:
        query = query.filter(Attendance.attendance_date >= date_from)
    
    if date_to:
        query = query.filter(Attendance.attendance_date <= date_to)
    
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    
    if status:
        query = query.filter(Attendance.attendance_status == status)
    
    # Order by date descending
    query = query.order_by(Attendance.attendance_date.desc(), Attendance.id.asc())
    
    total = query.count()
    attendance_records = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    attendance_responses = []
    for record in attendance_records:
        user = db.query(User).filter(User.id == record.user_id).first()
        attendance_responses.append(AttendanceListResponse(
            user_id=record.user_id,
            user_name=user.full_name or user.username if user else "Unknown",
            id=record.id,
            attendance_date=record.attendance_date,
            attendance_status=record.attendance_status,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            created_at=record.created_at
        ))
    
    total_pages = (total + size - 1) // size
    
    return {
        "items": attendance_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }



@router.post("/{user_id}/approve-leave")
async def approve_leave(
    user_id: int,
    attendance_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve leave request for attendance record
    """
    
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id,
        Attendance.user_id == user_id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Check access
    if current_user.hostel_id and attendance.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    attendance.leave_approved_by = current_user.id
    attendance.leave_approved_at = datetime.now()
    attendance.attendance_status = AttendanceStatus.EXCUSED
    
    db.commit()
    db.refresh(attendance)
    
    return {"message": "Leave approved successfully"}


@router.post("/quick-actions/mark-attendance/{user_id}")
async def quick_mark_attendance(
    user_id: int,
    attendance_data: QuickMarkAttendance,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick action to mark attendance for a student
    """
    
    # Verify student belongs to supervisor's hostel
    from app.core.roles import Role
    student = db.query(User).filter(
        User.id == user_id,
        User.role == Role.STUDENT.value
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if current_user.hostel_id and student.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if attendance already exists for today
    today = date.today()
    existing_attendance = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        Attendance.attendance_date == today
    ).first()
    
    if existing_attendance:
        existing_attendance.attendance_status = attendance_data.attendance_status
        existing_attendance.marked_by = current_user.id
        existing_attendance.updated_at = datetime.now()
    else:
        new_attendance = Attendance(
            user_id=user_id,
            hostel_id=student.hostel_id,
            attendance_date=today,
            attendance_status=attendance_data.attendance_status,
            marked_by=current_user.id
        )
        db.add(new_attendance)
    
    db.commit()
    
    return {"message": f"Attendance marked as {attendance_data.attendance_status.value}"}


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific attendance record details
    """
    
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Check access
    if current_user.hostel_id and attendance.hostel_id != current_user.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return attendance
