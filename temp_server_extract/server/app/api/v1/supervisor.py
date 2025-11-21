from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify user from JWT token"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
from app.schemas.complaint import (
    ComplaintResponse, ComplaintListResponse, ComplaintSearchParams,
    ComplaintUpdate, ComplaintAssignment, ComplaintResolution
)
from app.schemas.attendance import (
    AttendanceResponse, AttendanceListResponse, AttendanceCreate,
    AttendanceUpdate, AttendanceSearchParams
)
from app.schemas.leave_application import (
    LeaveApplicationListResponse, LeaveApprovalRequest, LeaveRejectionRequest
)
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.models.user import User
from app.models.complaint import Complaint
from app.models.attendance import Attendance
from app.models.leave_application import LeaveApplication
from app.models.enums import UserType, ComplaintStatus, AttendanceStatus, LeaveStatus, Priority

router = APIRouter()


def get_supervisor_user(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Get current supervisor user"""
    user = db.query(User).filter(User.id == current_user["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has supervisor, admin, or super_admin role
    allowed_types = [UserType.SUPERVISOR, UserType.ADMIN, UserType.SUPER_ADMIN]
    if user.user_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required"
        )
    return user


# Dashboard APIs
@router.get("/dashboard/metrics")
async def get_supervisor_dashboard_metrics(
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get supervisor dashboard metrics"""
    
    try:
        # Active complaints
        active_complaints = 0
        try:
            from sqlalchemy import or_
            active_complaints_query = db.query(Complaint).filter(
                or_(
                    Complaint.complaint_status == ComplaintStatus.OPEN,
                    Complaint.complaint_status == ComplaintStatus.IN_PROGRESS
                )
            )
            if supervisor.hostel_id:
                active_complaints_query = active_complaints_query.filter(Complaint.hostel_id == supervisor.hostel_id)
            active_complaints = active_complaints_query.count()
        except Exception as e:
            print(f"Error counting complaints: {e}")
        
        # Pending tasks (complaints assigned to supervisor)
        pending_tasks = 0
        try:
            pending_tasks = db.query(Complaint).filter(
                Complaint.assigned_to == supervisor.id,
                Complaint.complaint_status == ComplaintStatus.IN_PROGRESS
            ).count()
        except Exception as e:
            print(f"Error counting pending tasks: {e}")
        
        # Today's attendance
        today_attendance = 0
        try:
            from datetime import date
            today_attendance_query = db.query(Attendance).filter(
                Attendance.attendance_date == date.today()
            )
            if supervisor.hostel_id:
                today_attendance_query = today_attendance_query.filter(Attendance.hostel_id == supervisor.hostel_id)
            today_attendance = today_attendance_query.count()
        except Exception as e:
            print(f"Error counting attendance: {e}")
        
        # Students in hostel
        students_count = 0
        try:
            students_count_query = db.query(User).filter(
                User.user_type == UserType.STUDENT,
                User.is_active == True
            )
            if supervisor.hostel_id:
                students_count_query = students_count_query.filter(User.hostel_id == supervisor.hostel_id)
            students_count = students_count_query.count()
        except Exception as e:
            print(f"Error counting students: {e}")
        
        return {
            "active_complaints": active_complaints,
            "pending_tasks": pending_tasks,
            "today_attendance": today_attendance,
            "total_students": students_count,
            "hostel_id": supervisor.hostel_id
        }
    except Exception as e:
        print(f"Dashboard metrics error: {e}")
        return {
            "active_complaints": 0,
            "pending_tasks": 0,
            "today_attendance": 0,
            "total_students": 0,
            "hostel_id": supervisor.hostel_id,
            "error": "Unable to fetch metrics"
        }


# Complaint Handling APIs
@router.get("/complaints", response_model=PaginatedResponse[ComplaintListResponse])
async def get_complaints(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[ComplaintStatus] = None,
    priority: Optional[str] = None,
    assigned_to_me: bool = False,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get complaints with filtering"""
    
    query = db.query(Complaint)
    
    # Filter by hostel if supervisor is assigned to specific hostel
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
    
    # Convert to response format (you'll need to join with user and hostel tables)
    complaint_responses = []
    for complaint in complaints:
        user = db.query(User).filter(User.id == complaint.user_id).first()
        complaint_responses.append(ComplaintListResponse(
            id=complaint.id,
            complaint_title=complaint.complaint_title,
            complaint_category=complaint.complaint_category,
            complaint_status=complaint.complaint_status,
            priority=complaint.priority,
            user_id=complaint.user_id,
            user_name=user.name if user else "Unknown",
            hostel_id=complaint.hostel_id,
            hostel_name="Hostel Name",  # You'll need to join with hostel table
            room_number=complaint.room_number,
            created_at=complaint.created_at
        ))
    
    return PaginatedResponse.create(complaint_responses, total, page, size)


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
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
    
    # Check if supervisor has access to this complaint
    if supervisor.hostel_id and complaint.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return complaint


@router.put("/complaints/{complaint_id}/assign", response_model=MessageResponse)
async def assign_complaint(
    complaint_id: int,
    assignment: ComplaintAssignment,
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
    if assignment.role:
        from app.models.supervisor import Supervisor
        
        # Find supervisor with matching role in the same hostel
        supervisor_profile = db.query(Supervisor).join(
            User, Supervisor.user_id == User.id
        ).filter(
            Supervisor.role == assignment.role.lower(),
            Supervisor.status == "active"
        )
        
        # Filter by hostel if complaint has hostel_id
        if complaint.hostel_id:
            supervisor_profile = supervisor_profile.filter(
                Supervisor.hostel_id == complaint.hostel_id
            )
        
        supervisor_profile = supervisor_profile.first()
        
        if not supervisor_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No active {assignment.role} found for this hostel"
            )
        
        assignee_id = supervisor_profile.user_id
    
    # If assigned_to is provided, verify the user
    elif assignment.assigned_to:
        assignee = db.query(User).filter(User.id == assignment.assigned_to).first()
        if not assignee or assignee.user_type not in [UserType.STAFF, UserType.SUPERVISOR]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee"
            )
        assignee_id = assignment.assigned_to
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either assigned_to or role must be provided"
        )
    
    complaint.assigned_to = assignee_id
    complaint.complaint_status = ComplaintStatus.IN_PROGRESS
    db.commit()
    
    return MessageResponse(message="Complaint assigned successfully")


@router.put("/complaints/{complaint_id}/resolve", response_model=MessageResponse)
async def resolve_complaint(
    complaint_id: int,
    resolution: ComplaintResolution,
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
    if complaint.assigned_to != supervisor.id and supervisor.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only resolve complaints assigned to you"
        )
    
    complaint.complaint_status = ComplaintStatus.RESOLVED
    complaint.resolution_notes = resolution.resolution_notes
    complaint.resolution_attachments = resolution.resolution_attachments
    complaint.resolved_at = datetime.now()  # Use Python's datetime.now()
    
    db.commit()
    
    return MessageResponse(message="Complaint resolved successfully")


# Attendance Operations APIs
@router.get("/attendance", response_model=PaginatedResponse[AttendanceListResponse])
async def get_attendance_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user_id: Optional[int] = None,  # Integer ID
    status: Optional[AttendanceStatus] = None,
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
    
    # Order by user_id first, then by attendance_date (descending), then by id
    query = query.order_by(Attendance.user_id.asc(), Attendance.attendance_date.desc(), Attendance.id.asc())
    
    total = query.count()
    attendance_records = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format (user_id first, then attendance_id)
    attendance_responses = []
    for record in attendance_records:
        user = db.query(User).filter(User.id == record.user_id).first()
        attendance_responses.append(AttendanceListResponse(
            user_id=record.user_id,  # User ID first
            user_name=user.name if user else "Unknown",
            id=record.id,  # Attendance ID second
            attendance_date=record.attendance_date,
            attendance_status=record.attendance_status,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            created_at=record.created_at
        ))
    
    return PaginatedResponse.create(attendance_responses, total, page, size)


@router.post("/attendance/{user_id}/approve-leave", response_model=MessageResponse)
async def approve_leave(
    user_id: int,  # Integer ID
    attendance_id: int,  # Integer ID
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
    
    attendance.leave_approved_by = supervisor.id
    attendance.leave_approved_at = datetime.now()
    attendance.attendance_status = AttendanceStatus.EXCUSED
    
    db.commit()
    
    return MessageResponse(message="Leave approved successfully")


@router.get("/students", response_model=PaginatedResponse[UserResponse])
async def get_students(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get students in supervisor's hostel"""
    
    query = db.query(User).filter(User.user_type == UserType.STUDENT)
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(User.hostel_id == supervisor.hostel_id)
    
    # Search filter
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )
    
    total = query.count()
    students = query.offset((page - 1) * size).limit(size).all()
    
    return PaginatedResponse.create(students, total, page, size)


# Leave Application Management APIs
@router.get("/leave-applications", response_model=PaginatedResponse[LeaveApplicationListResponse])
async def get_leave_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[LeaveStatus] = None,
    pending_only: bool = False,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get leave applications for supervisor's hostel"""
    
    query = db.query(LeaveApplication).join(User, LeaveApplication.student_id == User.id)
    
    # Filter by hostel
    if supervisor.hostel_id:
        query = query.filter(User.hostel_id == supervisor.hostel_id)
    
    # Apply filters
    if status:
        query = query.filter(LeaveApplication.leave_status == status)
    
    if pending_only:
        query = query.filter(LeaveApplication.leave_status == LeaveStatus.PENDING)
    
    total = query.count()
    leave_applications = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format
    leave_responses = []
    for leave_app in leave_applications:
        student = db.query(User).filter(User.id == leave_app.student_id).first()
        leave_responses.append(LeaveApplicationListResponse(
            id=leave_app.id,
            student_id=leave_app.student_id,
            student_name=student.name if student else "Unknown",
            leave_start_date=leave_app.leave_start_date,
            leave_end_date=leave_app.leave_end_date,
            leave_reason=leave_app.leave_reason,
            leave_status=leave_app.leave_status,
            leave_type=leave_app.leave_type,
            emergency_contact=leave_app.emergency_contact,
            created_at=leave_app.created_at,
            duration_days=leave_app.leave_duration_days
        ))
    
    return PaginatedResponse.create(leave_responses, total, page, size)


@router.put("/leave-applications/{leave_id}/approve", response_model=MessageResponse)
async def approve_leave_application(
    leave_id: int,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Approve leave application"""
    
    leave_app = db.query(LeaveApplication).filter(LeaveApplication.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if student belongs to supervisor's hostel
    student = db.query(User).filter(User.id == leave_app.student_id).first()
    if supervisor.hostel_id and student.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if leave_app.leave_status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave application is not in pending status"
        )
    
    leave_app.leave_status = LeaveStatus.APPROVED
    leave_app.approved_by = supervisor.id
    leave_app.approved_at = datetime.now()
    
    db.commit()
    
    return MessageResponse(message="Leave application approved successfully")


@router.put("/leave-applications/{leave_id}/reject", response_model=MessageResponse)
async def reject_leave_application(
    leave_id: int,
    rejection_reason: str,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Reject leave application"""
    
    leave_app = db.query(LeaveApplication).filter(LeaveApplication.id == leave_id).first()
    if not leave_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if student belongs to supervisor's hostel
    student = db.query(User).filter(User.id == leave_app.student_id).first()
    if supervisor.hostel_id and student.hostel_id != supervisor.hostel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if leave_app.leave_status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave application is not in pending status"
        )
    
    leave_app.leave_status = LeaveStatus.REJECTED
    leave_app.approved_by = supervisor.id
    leave_app.approved_at = datetime.now()
    leave_app.rejection_reason = rejection_reason
    
    db.commit()
    
    return MessageResponse(message="Leave application rejected successfully")


# Quick Action Endpoints
@router.post("/quick-actions/mark-attendance/{user_id}", response_model=MessageResponse)
async def quick_mark_attendance(
    user_id: int,  # Integer ID
    attendance_status: AttendanceStatus,
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Quick action to mark attendance for a student"""
    
    # Verify student belongs to supervisor's hostel
    student = db.query(User).filter(
        User.id == user_id,
        User.user_type == UserType.STUDENT
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
    from datetime import date
    today = date.today()
    existing_attendance = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        Attendance.attendance_date == today
    ).first()
    
    if existing_attendance:
        existing_attendance.attendance_status = attendance_status
        existing_attendance.marked_by = supervisor.id
    else:
        new_attendance = Attendance(
            user_id=user_id,
            hostel_id=student.hostel_id,
            attendance_date=today,
            attendance_status=attendance_status,
            marked_by=supervisor.id
        )
        db.add(new_attendance)
    
    db.commit()
    
    return MessageResponse(message=f"Attendance marked as {attendance_status.value}")


@router.get("/dashboard/quick-stats")
async def get_quick_stats(
    supervisor: User = Depends(get_supervisor_user),
    db: Session = Depends(get_db)
):
    """Get quick statistics for supervisor dashboard"""
    
    from datetime import date, timedelta
    today = date.today()
    
    # Today's stats
    today_present_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == AttendanceStatus.PRESENT
    )
    if supervisor.hostel_id:
        today_present_query = today_present_query.filter(Attendance.hostel_id == supervisor.hostel_id)
    today_present = today_present_query.count()
    
    today_absent_query = db.query(Attendance).filter(
        Attendance.attendance_date == today,
        Attendance.attendance_status == AttendanceStatus.ABSENT
    )
    if supervisor.hostel_id:
        today_absent_query = today_absent_query.filter(Attendance.hostel_id == supervisor.hostel_id)
    today_absent = today_absent_query.count()
    
    # Pending approvals
    pending_leaves_query = db.query(LeaveApplication).join(User, LeaveApplication.student_id == User.id).filter(
        LeaveApplication.leave_status == LeaveStatus.PENDING
    )
    if supervisor.hostel_id:
        pending_leaves_query = pending_leaves_query.filter(User.hostel_id == supervisor.hostel_id)
    pending_leaves = pending_leaves_query.count()
    
    # Critical complaints
    from sqlalchemy import or_
    critical_complaints_query = db.query(Complaint).filter(
        Complaint.priority == Priority.CRITICAL,
        or_(
            Complaint.complaint_status == ComplaintStatus.OPEN,
            Complaint.complaint_status == ComplaintStatus.IN_PROGRESS
        )
    )
    if supervisor.hostel_id:
        critical_complaints_query = critical_complaints_query.filter(Complaint.hostel_id == supervisor.hostel_id)
    critical_complaints = critical_complaints_query.count()
    
    # Students on leave today
    students_on_leave_query = db.query(LeaveApplication).join(User, LeaveApplication.student_id == User.id).filter(
        LeaveApplication.leave_status == LeaveStatus.APPROVED,
        LeaveApplication.leave_start_date <= today,
        LeaveApplication.leave_end_date >= today
    )
    if supervisor.hostel_id:
        students_on_leave_query = students_on_leave_query.filter(User.hostel_id == supervisor.hostel_id)
    students_on_leave = students_on_leave_query.count()
    
    return {
        "today_present": today_present,
        "today_absent": today_absent,
        "pending_leaves": pending_leaves,
        "critical_complaints": critical_complaints,
        "students_on_leave": students_on_leave,
        "hostel_id": supervisor.hostel_id,
        "supervisor_name": supervisor.name,
        "date": today.isoformat()
    }