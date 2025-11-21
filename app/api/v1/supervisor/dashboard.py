"""
Supervisor Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import date, datetime, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.leave import LeaveRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Supervisor Dashboard"])


@router.get("/metrics")
async def get_supervisor_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get supervisor dashboard metrics
    
    Returns:
    - active_complaints: Count of open/in_progress complaints
    - pending_tasks: Count of complaints assigned to supervisor
    - today_attendance: Count of today's attendance records
    - total_students: Count of active students in hostel
    """
    
    try:
        # Active complaints (open or in_progress)
        active_complaints = 0
        try:
            active_complaints_query = db.query(Complaint).filter(
                or_(
                    Complaint.status == ComplaintStatus.PENDING,
                    Complaint.status == ComplaintStatus.IN_PROGRESS
                )
            )
            if current_user.hostel_id:
                active_complaints_query = active_complaints_query.filter(
                    Complaint.hostel_name == db.query(User).filter(
                        User.hostel_id == current_user.hostel_id
                    ).first().hostel.name if hasattr(current_user, 'hostel') else None
                )
            active_complaints = active_complaints_query.count()
        except Exception as e:
            print(f"Error counting complaints: {e}")
        
        # Pending tasks (complaints assigned to supervisor)
        pending_tasks = 0
        try:
            pending_tasks = db.query(Complaint).filter(
                Complaint.assigned_to_email == current_user.email,
                Complaint.status == ComplaintStatus.IN_PROGRESS
            ).count()
        except Exception as e:
            print(f"Error counting pending tasks: {e}")
        
        # Today's attendance
        today_attendance = 0
        try:
            today = date.today()
            today_attendance_query = db.query(Attendance).filter(
                Attendance.attendance_date == today
            )
            if current_user.hostel_id:
                today_attendance_query = today_attendance_query.filter(
                    Attendance.hostel_id == current_user.hostel_id
                )
            today_attendance = today_attendance_query.count()
        except Exception as e:
            print(f"Error counting attendance: {e}")
        
        # Students in hostel
        students_count = 0
        try:
            from app.core.roles import Role
            students_count_query = db.query(User).filter(
                User.role == Role.STUDENT.value,
                User.is_active == True
            )
            if current_user.hostel_id:
                students_count_query = students_count_query.filter(
                    User.hostel_id == current_user.hostel_id
                )
            students_count = students_count_query.count()
        except Exception as e:
            print(f"Error counting students: {e}")
        
        return {
            "active_complaints": active_complaints,
            "pending_tasks": pending_tasks,
            "today_attendance": today_attendance,
            "total_students": students_count,
            "hostel_id": current_user.hostel_id
        }
    except Exception as e:
        print(f"Dashboard metrics error: {e}")
        return {
            "active_complaints": 0,
            "pending_tasks": 0,
            "today_attendance": 0,
            "total_students": 0,
            "hostel_id": current_user.hostel_id,
            "error": "Unable to fetch metrics"
        }


@router.get("/quick-stats")
async def get_quick_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick statistics for supervisor dashboard
    
    Returns:
    - today_present: Students present today
    - today_absent: Students absent today
    - pending_leaves: Pending leave applications
    - critical_complaints: Critical priority complaints
    - students_on_leave: Students currently on approved leave
    """
    
    today = date.today()
    
    # Today's present count
    today_present_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == AttendanceStatus.PRESENT
    )
    if current_user.hostel_id:
        today_present_query = today_present_query.filter(
            Attendance.hostel_id == current_user.hostel_id
        )
    today_present = today_present_query.count()
    
    # Today's absent count
    today_absent_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == AttendanceStatus.ABSENT
    )
    if current_user.hostel_id:
        today_absent_query = today_absent_query.filter(
            Attendance.hostel_id == current_user.hostel_id
        )
    today_absent = today_absent_query.count()
    
    # Pending leave applications
    pending_leaves_query = db.query(LeaveRequest).filter(
        LeaveRequest.status == "PENDING"
    )
    if current_user.hostel_id:
        pending_leaves_query = pending_leaves_query.filter(
            LeaveRequest.hostel_id == current_user.hostel_id
        )
    pending_leaves = pending_leaves_query.count()
    
    # Critical complaints
    from app.models.complaint import ComplaintPriority
    critical_complaints_query = db.query(Complaint).filter(
        Complaint.priority == ComplaintPriority.URGENT,
        or_(
            Complaint.status == ComplaintStatus.PENDING,
            Complaint.status == ComplaintStatus.IN_PROGRESS
        )
    )
    critical_complaints = critical_complaints_query.count()
    
    # Students on leave today
    students_on_leave_query = db.query(LeaveRequest).filter(
        LeaveRequest.status == "APPROVED",
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today
    )
    if current_user.hostel_id:
        students_on_leave_query = students_on_leave_query.filter(
            LeaveRequest.hostel_id == current_user.hostel_id
        )
    students_on_leave = students_on_leave_query.count()
    
    return {
        "today_present": today_present,
        "today_absent": today_absent,
        "pending_leaves": pending_leaves,
        "critical_complaints": critical_complaints,
        "students_on_leave": students_on_leave,
        "hostel_id": current_user.hostel_id,
        "supervisor_name": current_user.full_name or current_user.username,
        "date": today.isoformat()
    }
