from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from sqlalchemy import select

from app.core.database import get_db
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
    db: AsyncSession = Depends(get_db)
):
    """List all complaints with advanced filtering"""
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
    db: AsyncSession = Depends(get_db)
):
    """Get detailed complaint information"""
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
    db: AsyncSession = Depends(get_db)
):
    """Update complaint details"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.update_complaint(complaint_id, update_data)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@router.post("/{complaint_id}/reassign", response_model=ComplaintResponse)
async def reassign_complaint(
    complaint_id: int,
    assignment_data: ComplaintAssignment,
    db: AsyncSession = Depends(get_db)
):
    """Reassign complaint to different supervisor"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    complaint = await service.reassign_complaint(
        complaint_id,
        assignment_data.assigned_to_name,
        assignment_data.assigned_to_email
    )
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint


@router.get("/analytics/overview", response_model=ComplaintAnalytics)
async def get_complaint_analytics(
    hostel_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive complaint analytics"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    analytics = await service.get_analytics(hostel_name, start_date, end_date)
    
    return analytics


@router.get("/analytics/cross-hostel")
async def get_cross_hostel_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics across all hostels for identifying systemic issues"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    # Get unique hostel names
    query = select(Complaint.hostel_name).distinct()
    result = await db.execute(query)
    hostels = [row[0] for row in result.all()]
    
    cross_hostel_data = []
    
    for hostel_name in hostels:
        analytics = await service.get_analytics(hostel_name, start_date, end_date)
        
        cross_hostel_data.append({
            "hostel_name": hostel_name,
            "analytics": analytics
        })
    
    # Identify systemic issues
    category_counts = {}
    for hostel_data in cross_hostel_data:
        for category, count in hostel_data['analytics']['category_distribution'].items():
            category_counts[category] = category_counts.get(category, 0) + count
    
    systemic_issues = sorted(
        [{"category": k, "total_complaints": v} for k, v in category_counts.items()],
        key=lambda x: x['total_complaints'],
        reverse=True
    )
    
    return {
        "hostel_analytics": cross_hostel_data,
        "systemic_issues": systemic_issues,
        "total_hostels": len(hostels)
    }


@router.get("/analytics/supervisor-performance")
async def get_all_supervisor_performance(
    hostel_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for all supervisors"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
    
    # Get unique supervisor emails
    query = select(Complaint.assigned_to_email, Complaint.assigned_to_name).distinct().where(
        Complaint.assigned_to_email.isnot(None)
    )
    
    if hostel_name:
        query = query.where(Complaint.hostel_name.ilike(f"%{hostel_name}%"))
    
    result = await db.execute(query)
    supervisors = result.all()
    
    performance_data = []
    
    for supervisor_email, supervisor_name in supervisors:
        if supervisor_email:
            performance = await service.get_supervisor_performance(
                supervisor_email,
                start_date,
                end_date
            )
            performance_data.append(performance)
    
    # Sort by average resolution time
    performance_data.sort(
        key=lambda x: x['average_resolution_time_hours'] if x['average_resolution_time_hours'] else float('inf')
    )
    
    return {
        "total_supervisors": len(performance_data),
        "supervisors": performance_data
    }


@router.get("/analytics/sla-violations")
async def get_sla_violations(
    hostel_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get complaints that have violated SLA"""
    now = datetime.utcnow()
    
    query = select(Complaint).where(
        Complaint.sla_deadline.isnot(None),
        Complaint.sla_deadline < now,
        Complaint.status.notin_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
    )
    
    if hostel_name:
        query = query.where(Complaint.hostel_name.ilike(f"%{hostel_name}%"))
    
    query = query.order_by(Complaint.sla_deadline.asc())
    
    result = await db.execute(query)
    violations = result.scalars().all()
    
    violation_data = []
    
    for complaint in violations:
        hours_overdue = (now - complaint.sla_deadline).total_seconds() / 3600
        
        violation_data.append({
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
    
    return {
        "total_violations": len(violation_data),
        "violations": violation_data
    }


@router.get("/analytics/escalated")
async def get_escalated_complaints(
    hostel_name: Optional[str] = Query(None),
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get all escalated complaints"""
    filters = ComplaintFilter(
        hostel_name=hostel_name,
        is_escalated=True,
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


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a complaint"""
    repository = ComplaintRepository(db)
    
    complaint = await repository.get_by_id(complaint_id)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    await repository.delete(complaint)
    
    return None