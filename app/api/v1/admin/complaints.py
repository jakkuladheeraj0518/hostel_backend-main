from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from sqlalchemy import select
 
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_repository_context, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
from app.repositories.complaint_repository import ComplaintRepository
from app.services.complaint_service import ComplaintService
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.complaint import (
    ComplaintResponse,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintFilter,
    ComplaintAssignment,
    ComplaintUpdate,
    ComplaintAnalytics
)
 
router = APIRouter(prefix="/admin/complaints", tags=["Admin Complaints"])
 
 
# ------------------------------------------------------------------------------------
# LIST ALL COMPLAINTS
# ------------------------------------------------------------------------------------
@router.get("/", response_model=ComplaintListResponse)
async def list_all_complaints(
    hostel_name: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_email: Optional[str] = None,
    student_email: Optional[str] = None,
    is_escalated: Optional[bool] = None,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    filters = ComplaintFilter(
        hostel_name=hostel_name,
        category=category,
        status=status_filter,
        priority=priority,
        assigned_to_email=assigned_to_email,
        student_email=student_email,
        is_escalated=is_escalated,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
 
    service = ComplaintService(ComplaintRepository(db))
    complaints, total = await service.list_complaints(filters)
 
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "complaints": complaints
    }
 
 
# ------------------------------------------------------------------------------------
# GET SINGLE COMPLAINT
# ------------------------------------------------------------------------------------
@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
async def get_complaint(complaint_id: int,
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)):
    service = ComplaintService(ComplaintRepository(db))
    result = await service.get_complaint_with_details(complaint_id)
 
    if not result:
        raise HTTPException(404, "Complaint not found")
 
    complaint = result["complaint"]
 
    return {
        **complaint.__dict__,
        "attachments": result["attachments"],
        "notes": result["notes"]
    }
 
 
# ------------------------------------------------------------------------------------
# UPDATE COMPLAINT
# ------------------------------------------------------------------------------------
@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(complaint_id: int, update_data: ComplaintUpdate,current_user: User = Depends(role_required(Role.ADMIN)), db: Session = Depends(get_db)):
    service = ComplaintService(ComplaintRepository(db))
    complaint = await service.update_complaint(complaint_id, update_data)
 
    if not complaint:
        raise HTTPException(404, "Complaint not found")
 
    return complaint
 
 
# ------------------------------------------------------------------------------------
# REASSIGN COMPLAINT
# ------------------------------------------------------------------------------------
@router.post("/{complaint_id}/reassign", response_model=ComplaintResponse)
async def reassign_complaint(complaint_id: int, assignment_data: ComplaintAssignment, current_user: User = Depends(role_required(Role.ADMIN)),db: Session = Depends(get_db)):
    service = ComplaintService(ComplaintRepository(db))
 
    complaint = await service.reassign_complaint(
        complaint_id,
        assignment_data.assigned_to_name,
        assignment_data.assigned_to_email
    )
 
    if not complaint:
        raise HTTPException(404, "Complaint not found")
 
    return complaint
 
 
# ------------------------------------------------------------------------------------
# ANALYTICS — OVERVIEW
# ------------------------------------------------------------------------------------
@router.get("/analytics/overview", response_model=ComplaintAnalytics)
async def get_complaint_analytics(
    hostel_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    service = ComplaintService(ComplaintRepository(db))
    result = await service.get_analytics(hostel_name, start_date, end_date)
    return result
 
 
# ------------------------------------------------------------------------------------
# ANALYTICS — CROSS HOSTEL
# ------------------------------------------------------------------------------------
@router.get("/analytics/cross-hostel")
async def get_cross_hostel_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    service = ComplaintService(ComplaintRepository(db))
 
    hostels = [row[0] for row in db.execute(select(Complaint.hostel_name).distinct()).all()]
    cross_hostel_data = []
 
    for hostel_name in hostels:
        analytics = await service.get_analytics(hostel_name, start_date, end_date)
        cross_hostel_data.append({"hostel_name": hostel_name, "analytics": analytics})
 
    category_counts = {}
    for hostel_data in cross_hostel_data:
        for category, count in hostel_data["analytics"]["category_distribution"].items():
            category_counts[category] = category_counts.get(category, 0) + count
 
    systemic_issues = sorted(
        [{"category": k, "total_complaints": v} for k, v in category_counts.items()],
        key=lambda x: x["total_complaints"],
        reverse=True
    )
 
    return {
        "hostel_analytics": cross_hostel_data,
        "systemic_issues": systemic_issues,
        "total_hostels": len(hostels)
    }
 
 
# ------------------------------------------------------------------------------------
# ANALYTICS — SUPERVISOR PERFORMANCE
# ------------------------------------------------------------------------------------
@router.get("/analytics/supervisor-performance")
async def get_all_supervisor_performance(
    hostel_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    service = ComplaintService(ComplaintRepository(db))
 
    query = select(
        Complaint.assigned_to_email,
        Complaint.assigned_to_name
    ).distinct().where(Complaint.assigned_to_email.isnot(None))
 
    if hostel_name:
        query = query.where(Complaint.hostel_name.ilike(f"%{hostel_name}%"))
 
    supervisors = db.execute(query).all()
    performance_data = []
 
    for supervisor_email, supervisor_name in supervisors:
        if not supervisor_email:
            continue
 
        performance = await service.get_supervisor_performance(
            supervisor_email,
            start_date,
            end_date
        )
 
        performance["supervisor_name"] = supervisor_name
        performance_data.append(performance)
 
    performance_data.sort(
        key=lambda x: x["average_resolution_time_hours"] or float("inf")
    )
 
    return {
        "total_supervisors": len(performance_data),
        "supervisors": performance_data
    }
 
 
# ------------------------------------------------------------------------------------
# ANALYTICS — SLA VIOLATIONS
# ------------------------------------------------------------------------------------
@router.get("/analytics/sla-violations")
async def get_sla_violations(
    hostel_name: Optional[str] = Query(None),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
 
    query = select(Complaint).where(
        Complaint.sla_deadline.isnot(None),
        Complaint.sla_deadline < now,
        Complaint.status.notin_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
    )
 
    if hostel_name:
        query = query.where(Complaint.hostel_name.ilike(f"%{hostel_name}%"))
 
    violations = db.execute(query.order_by(Complaint.sla_deadline.asc())).scalars().all()
 
    data = []
    for complaint in violations:
        hours_overdue = (now - complaint.sla_deadline).total_seconds() / 3600
        data.append({
            "id": complaint.id,
            "title": complaint.title,
            "category": complaint.category.value,
            "priority": complaint.priority.value,
            "status": complaint.status.value,
            "hostel_name": complaint.hostel_name,
            "assigned_to_email": complaint.assigned_to_email,
            "sla_deadline": complaint.sla_deadline,
            "hours_overdue": round(hours_overdue, 2),
            "created_at": complaint.created_at
        })
 
    return {"total_violations": len(data), "violations": data}
 
 
# ------------------------------------------------------------------------------------
# ANALYTICS — ESCALATED COMPLAINTS
# ------------------------------------------------------------------------------------
@router.get("/analytics/escalated")
async def get_escalated_complaints(
    hostel_name: Optional[str] = Query(None),
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    filters = ComplaintFilter(
        hostel_name=hostel_name,
        is_escalated=True,
        page=page,
        page_size=page_size
    )
 
    service = ComplaintService(ComplaintRepository(db))
    complaints, total = await service.list_complaints(filters)
 
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "complaints": complaints
    }
 
 
# ------------------------------------------------------------------------------------
# DELETE COMPLAINT
# ------------------------------------------------------------------------------------
@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(complaint_id: int,current_user: User = Depends(role_required(Role.ADMIN)), db: Session = Depends(get_db)):
    repo = ComplaintRepository(db)
    complaint = await repo.get_by_id(complaint_id)
 
    if not complaint:
        raise HTTPException(404, "Complaint not found")
 
    success = await repo.delete(complaint_id)
    if not success:
        raise HTTPException(500, "Failed to delete complaint")
   
    return None
 