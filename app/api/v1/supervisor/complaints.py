from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

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
from app.models.complaint import ComplaintStatus
from app.repositories.complaint_repository import ComplaintRepository
from app.services.complaint_service import ComplaintService
from app.schemas.complaint import (
    ComplaintResponse,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintFilter,
    ComplaintAssignment,
    ComplaintResolution,
    ComplaintUpdate,
    ComplaintNoteCreate,
    SupervisorPerformance
)

router = APIRouter(prefix="/supervisor/complaints", tags=["Supervisor Complaints"])


@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    hostel_name: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_me: bool = False,
    supervisor_email: str = Header(None, alias="X-User-Email"),
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """List complaints for supervisor"""
    filters = ComplaintFilter(
        hostel_name=hostel_name,
        category=category,
        status=status_filter,
        priority=priority,
        assigned_to_email=supervisor_email if assigned_to_me else None,
        page=page,
        page_size=page_size
    )
    
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaints, total = await service.list_complaints(filters)
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "complaints": complaints
    }


@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
async def get_complaint(
    complaint_id: int,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Get complaint details"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    result = await service.get_complaint_with_details(complaint_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint = result["complaint"]
    
    return {
        **complaint.__dict__,
        "attachments": result["attachments"],
        "notes": result["notes"]
    }


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    update_data: ComplaintUpdate,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Update complaint details"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.update_complaint(complaint_id, update_data)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@router.post("/{complaint_id}/assign", response_model=ComplaintResponse)
async def assign_complaint(
    complaint_id: int,
    assignment_data: ComplaintAssignment,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Assign complaint to supervisor/staff"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.assign_complaint(complaint_id, assignment_data)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@router.post("/{complaint_id}/resolve", response_model=ComplaintResponse)
async def resolve_complaint(
    complaint_id: int,
    resolution_data: ComplaintResolution,
    supervisor_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Mark complaint as resolved"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.get_complaint(complaint_id)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Verify assignment (allow if not assigned or assigned to this supervisor)
    if complaint.assigned_to_email and complaint.assigned_to_email != supervisor_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only resolve complaints assigned to you"
        )
    
    if complaint.status not in [ComplaintStatus.IN_PROGRESS, ComplaintStatus.REOPENED, ComplaintStatus.PENDING]:
        raise HTTPException(
            status_code=400,
            detail="Only pending, in-progress or reopened complaints can be resolved"
        )
    
    complaint = await service.resolve_complaint(complaint_id, resolution_data)
    return complaint


@router.post("/{complaint_id}/close", response_model=ComplaintResponse)
async def close_complaint(
    complaint_id: int,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Close a resolved complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.get_complaint(complaint_id)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    try:
        complaint = await service.close_complaint(complaint_id)
        return complaint
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{complaint_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_note(
    complaint_id: int,
    note: str,
    is_internal: bool = True,
    user_name: str = Header(..., alias="X-User-Name"),
    user_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Add internal or public note to complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.get_complaint(complaint_id)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    note_data = ComplaintNoteCreate(
        note=note,
        user_name=user_name,
        user_email=user_email,
        is_internal=is_internal
    )
    
    created_note = await service.add_note(complaint_id, note_data)
    
    return {
        "message": "Note added successfully",
        "note_id": created_note.id
    }


@router.get("/analytics/performance", response_model=SupervisorPerformance)
async def get_my_performance(
    supervisor_email: str = Header(..., alias="X-User-Email"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Get personal performance metrics"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    performance = await service.get_supervisor_performance(
        supervisor_email,
        start_date,
        end_date
    )
    
    return performance


@router.get("/analytics/unresolved")
async def get_unresolved_complaints(
    supervisor_email: str = Header(..., alias="X-User-Email"),
    hostel_name: Optional[str] = None,
    current_user: User = Depends(role_required(Role.SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    """Get unresolved complaints with aging information"""
    filters = ComplaintFilter(
        hostel_name=hostel_name,
        assigned_to_email=supervisor_email,
        page=1,
        page_size=100
    )
    
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaints, total = await service.list_complaints(filters)
    
    # Filter unresolved
    unresolved = [
        c for c in complaints 
        if c.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]
    ]
    
    # Calculate aging
    now = datetime.utcnow()
    aging_data = []
    
    for complaint in unresolved:
        age_hours = (now - complaint.created_at).total_seconds() / 3600
        sla_breached = complaint.sla_deadline and now > complaint.sla_deadline
        
        aging_data.append({
            "id": complaint.id,
            "title": complaint.title,
            "category": complaint.category.value,
            "priority": complaint.priority.value,
            "status": complaint.status.value,
            "age_hours": round(age_hours, 2),
            "sla_deadline": complaint.sla_deadline,
            "sla_breached": sla_breached,
            "created_at": complaint.created_at
        })
    
    # Sort by age descending
    aging_data.sort(key=lambda x: x['age_hours'], reverse=True)
    
    return {
        "total_unresolved": len(aging_data),
        "complaints": aging_data
    }