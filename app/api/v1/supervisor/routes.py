"""
Supervisor Routes
All supervisor-specific endpoints for hostel management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.complaint import Complaint
from app.models.reports import Attendance  # Use Attendance from reports (the one exported in __init__)
from app.models.leave import LeaveRequest  # Correct model name

router = APIRouter()


def get_supervisor_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify current user is a supervisor, admin, or super_admin"""
    allowed_types = ["supervisor", "admin", "super_admin"]
    
    if current_user.user_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required"
        )
    return current_user


# ==================== DASHBOARD APIs ====================

@router.get("/dashboard/metrics")
async def get_supervisor_dashboard_metrics(
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get supervisor dashboard metrics"""
    
    try:
        # Active complaints
        active_complaints_query = db.query(Complaint).filter(
            or_(
                Complaint.complaint_status == "open",
                Complaint.complaint_status == "in_progress"
            )
        )
        if supervisor.hostel_id:
            active_complaints_query = active_complaints_query.filter(Complaint.hostel_id == supervisor.hostel_id)
        active_complaints = active_complaints_query.count()
        
        # Pending tasks (complaints assigned to supervisor)
        pending_tasks = db.query(Complaint).filter(
            Complaint.assigned_to == supervisor.id,
            Complaint.complaint_status == "in_progress"
        ).count()
        
        # Today's attendance
        today_attendance_query = db.query(Attendance).filter(
            Attendance.attendance_date == date.today()
        )
        if supervisor.hostel_id:
            today_attendance_query = today_attendance_query.filter(Attendance.hostel_id == supervisor.hostel_id)
        today_attendance = today_attendance_query.count()
        
        # Students in hostel
        students_count_query = db.query(User).filter(
            User.user_type == "student",
            User.is_active == True
        )
        if supervisor.hostel_id:
            students_count_query = students_count_query.filter(User.hostel_id == supervisor.hostel_id)
        students_count = students_count_query.count()
        
        return {
            "active_complaints": active_complaints,
            "pending_tasks": pending_tasks,
            "today_attendance": today_attendance,
            "total_students": students_count,
            "hostel_id": str(supervisor.hostel_id) if supervisor.hostel_id else None
        }
    except Exception as e:
        print(f"Dashboard metrics error: {e}")
        return {
            "active_complaints": 0,
            "pending_tasks": 0,
            "today_attendance": 0,
            "total_students": 0,
            "hostel_id": str(supervisor.hostel_id) if supervisor.hostel_id else None,
            "error": "Unable to fetch metrics"
        }


@router.get("/dashboard/quick-stats")
async def get_quick_stats(
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get quick statistics for supervisor dashboard"""
    
    today = date.today()
    
    # Today's present count
    today_present_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == "present"
    )
    if supervisor.hostel_id:
        today_present_query = today_present_query.filter(Attendance.hostel_id == supervisor.hostel_id)
    today_present = today_present_query.count()
    
    # Today's absent count
    today_absent_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == "absent"
    )
    if supervisor.hostel_id:
        today_absent_query = today_absent_query.filter(Attendance.hostel_id == supervisor.hostel_id)
    today_absent = today_absent_query.count()
    
    # Pending leave applications
    pending_leaves_query = db.query(LeaveRequest).filter(LeaveRequest.status == "PENDING")
    if supervisor.hostel_id:
        pending_leaves_query = pending_leaves_query.filter(LeaveRequest.hostel_id == supervisor.hostel_id)
    pending_leaves = pending_leaves_query.count()
    
    # Critical complaints
    critical_complaints_query = db.query(Complaint).filter(
        Complaint.priority == "critical",
        or_(
            Complaint.complaint_status == "open",
            Complaint.complaint_status == "in_progress"
        )
    )
    if supervisor.hostel_id:
        critical_complaints_query = critical_complaints_query.filter(Complaint.hostel_id == supervisor.hostel_id)
    critical_complaints = critical_complaints_query.count()
    
    # Students on leave today
    students_on_leave_query = db.query(LeaveRequest).filter(
        LeaveRequest.status == "APPROVED",
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today
    )
    if supervisor.hostel_id:
        students_on_leave_query = students_on_leave_query.filter(LeaveRequest.hostel_id == supervisor.hostel_id)
    students_on_leave = students_on_leave_query.count()
    
    return {
        "today_present": today_present,
        "today_absent": today_absent,
        "pending_leaves": pending_leaves,
        "critical_complaints": critical_complaints,
        "students_on_leave": students_on_leave,
        "hostel_id": str(supervisor.hostel_id) if supervisor.hostel_id else None,
        "supervisor_name": supervisor.name,
        "date": today.isoformat()
    }


# ==================== COMPLAINT MANAGEMENT APIs ====================

@router.get("/complaints")
async def get_complaints(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_me: bool = False,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get complaints with filtering"""
    
    query = db.query(Complaint)
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(Complaint.hostel_id == supervisor.hostel_id)
    
    # Apply filters
    if status:
        query = query.filter(Complaint.complaint_status == status)
    
    if priority:
        query = query.filter(Complaint.priority == priority)
    
    if assigned_to_me:
        query = query.filter(Complaint.assigned_to == supervisor.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    complaints = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    complaint_responses = []
    for complaint in complaints:
        user = db.query(User).filter(User.id == complaint.user_id).first()
        complaint_responses.append({
            "id": complaint.id,
            "complaint_title": complaint.complaint_title,
            "complaint_category": complaint.complaint_category,
            "complaint_status": complaint.complaint_status,
            "priority": complaint.priority,
            "user_id": complaint.user_id,
            "user_name": user.name if user else "Unknown",
            "hostel_id": str(complaint.hostel_id) if complaint.hostel_id else None,
            "room_number": complaint.room_number,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None
        })
    
    return {
        "items": complaint_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "has_next": page * size < total,
        "has_prev": page > 1
    }


@router.get("/complaints/{complaint_id}")
async def get_complaint(
    complaint_id: int,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get complaint details"""
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check access
    if supervisor.hostel_id and complaint.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "id": complaint.id,
        "complaint_title": complaint.complaint_title,
        "complaint_description": complaint.complaint_description,
        "complaint_category": complaint.complaint_category,
        "complaint_status": complaint.complaint_status,
        "priority": complaint.priority,
        "user_id": complaint.user_id,
        "hostel_id": str(complaint.hostel_id) if complaint.hostel_id else None,
        "room_number": complaint.room_number,
        "location_details": complaint.location_details,
        "assigned_to": complaint.assigned_to,
        "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None,
        "attachments": complaint.attachments,
        "resolution_notes": complaint.resolution_notes,
        "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
        "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None
    }


@router.put("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: int,
    role: Optional[str] = None,
    assigned_to: Optional[int] = None,
    notes: Optional[str] = None,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Assign complaint to staff member by user ID or role"""
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check access
    if supervisor.hostel_id and complaint.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    assignee_id = None
    
    # If role is provided, find a supervisor with that role
    if role:
        # Find supervisor with matching role in the same hostel
        supervisor_user = db.query(User).filter(
            User.user_type == "supervisor",
            User.is_active == True
        )
        
        if complaint.hostel_id:
            supervisor_user = supervisor_user.filter(User.hostel_id == complaint.hostel_id)
        
        supervisor_user = supervisor_user.first()
        
        if not supervisor_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No active supervisor found for this hostel"
            )
        
        assignee_id = supervisor_user.id
    
    # If assigned_to is provided, verify the user
    elif assigned_to:
        assignee = db.query(User).filter(User.id == assigned_to).first()
        if not assignee or assignee.user_type not in ["staff", "supervisor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee"
            )
        assignee_id = assigned_to
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either assigned_to or role must be provided"
        )
    
    complaint.assigned_to = assignee_id
    complaint.complaint_status = "in_progress"
    if notes:
        complaint.resolution_notes = notes
    
    db.commit()
    
    return {"message": "Complaint assigned successfully"}


@router.put("/complaints/{complaint_id}/resolve")
async def resolve_complaint(
    complaint_id: int,
    resolution_notes: str,
    resolution_attachments: Optional[str] = None,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Resolve complaint"""
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if supervisor can resolve this complaint
    if complaint.assigned_to != supervisor.id and supervisor.user_type not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only resolve complaints assigned to you"
        )
    
    complaint.complaint_status = "resolved"
    complaint.resolution_notes = resolution_notes
    complaint.resolution_attachments = resolution_attachments
    complaint.resolved_at = datetime.now()
    
    db.commit()
    
    return {"message": "Complaint resolved successfully"}


# ==================== ATTENDANCE OPERATIONS APIs ====================

@router.get("/attendance")
async def get_attendance_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get attendance records"""
    
    query = db.query(Attendance)
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(Attendance.hostel_id == supervisor.hostel_id)
    
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
    query = query.order_by(Attendance.attendance_date.desc())
    
    total = query.count()
    attendance_records = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    attendance_responses = []
    for record in attendance_records:
        user = db.query(User).filter(User.id == record.user_id).first()
        attendance_responses.append({
            "user_id": record.user_id,
            "user_name": user.name if user else "Unknown",
            "id": record.id,
            "attendance_date": record.attendance_date.isoformat() if record.attendance_date else None,
            "attendance_status": record.attendance_status,
            "check_in_time": record.check_in_time.isoformat() if record.check_in_time else None,
            "check_out_time": record.check_out_time.isoformat() if record.check_out_time else None,
            "created_at": record.created_at.isoformat() if record.created_at else None
        })
    
    return {
        "items": attendance_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "has_next": page * size < total,
        "has_prev": page > 1
    }


@router.post("/attendance/{user_id}/approve-leave")
async def approve_leave(
    user_id: int,
    attendance_id: int = Query(...),
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Approve leave request"""
    
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
    if supervisor.hostel_id and attendance.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    attendance.attendance_status = "excused"
    
    db.commit()
    
    return {"message": "Leave approved successfully"}


@router.post("/quick-actions/mark-attendance/{user_id}")
async def quick_mark_attendance(
    user_id: int,
    attendance_status: str,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Quick action to mark attendance for a student"""
    
    # Verify student belongs to supervisor's hostel
    student = db.query(User).filter(
        User.id == user_id,
        User.user_type == "student"
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if supervisor.hostel_id and student.hostel_id != supervisor.hostel_id:
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
        existing_attendance.attendance_status = attendance_status
    else:
        new_attendance = Attendance(
            user_id=user_id,
            hostel_id=student.hostel_id,
            attendance_date=today,
            attendance_status=attendance_status
        )
        db.add(new_attendance)
    
    db.commit()
    
    return {"message": f"Attendance marked as {attendance_status}"}


# ==================== LEAVE APPLICATION MANAGEMENT APIs ====================

@router.get("/leave-applications")
async def get_leave_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    pending_only: bool = False,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get leave applications for supervisor's hostel"""
    
    query = db.query(LeaveRequest)
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(LeaveRequest.hostel_id == supervisor.hostel_id)
    
    # Apply filters
    if status:
        query = query.filter(LeaveRequest.status == status.upper())
    
    if pending_only:
        query = query.filter(LeaveRequest.status == "PENDING")
    
    total = query.count()
    leave_applications = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    leave_responses = []
    for leave_app in leave_applications:
        student = db.query(User).filter(User.id == leave_app.student_id).first()
        
        # Calculate duration
        duration_days = 0
        if leave_app.start_date and leave_app.end_date:
            duration_days = (leave_app.end_date - leave_app.start_date).days + 1
        
        leave_responses.append({
            "id": leave_app.id,
            "student_id": leave_app.student_id,
            "student_name": student.name if student else "Unknown",
            "start_date": leave_app.start_date.isoformat() if leave_app.start_date else None,
            "end_date": leave_app.end_date.isoformat() if leave_app.end_date else None,
            "reason": leave_app.reason,
            "status": leave_app.status,
            "duration_days": duration_days
        })
    
    return {
        "items": leave_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "has_next": page * size < total,
        "has_prev": page > 1
    }


@router.put("/leave-applications/{leave_id}/approve")
async def approve_leave_application(
    leave_id: int,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Approve leave application"""
    
    leave_app = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if leave belongs to supervisor's hostel
    if supervisor.hostel_id and leave_app.hostel_id != supervisor.hostel_id:
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
    
    return {
        "message": "Leave application approved successfully",
        "success": True
    }


@router.put("/leave-applications/{leave_id}/reject")
async def reject_leave_application(
    leave_id: int,
    rejection_reason: str = Query(..., min_length=10),
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Reject leave application"""
    
    leave_app = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if leave belongs to supervisor's hostel
    if supervisor.hostel_id and leave_app.hostel_id != supervisor.hostel_id:
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
    
    db.commit()
    
    return {
        "message": "Leave application rejected successfully",
        "success": True
    }


# ==================== STUDENT MANAGEMENT APIs ====================

@router.get("/students")
async def get_students(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get students in supervisor's hostel"""
    
    query = db.query(User).filter(User.user_type == "student")
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(User.hostel_id == supervisor.hostel_id)
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    students = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    student_responses = []
    for student in students:
        student_responses.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "user_type": student.user_type,
            "hostel_id": str(student.hostel_id) if student.hostel_id else None,
            "is_active": student.is_active,
            "is_verified": student.is_verified,
            "created_at": student.created_at.isoformat() if student.created_at else None
        })
    
    return {
        "items": student_responses,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "has_next": page * size < total,
        "has_prev": page > 1
    }
