"""
Admin Maintenance Request Management
Provides CRUD operations for maintenance requests with categorization, priority, and status tracking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.roles import Role
from app.api.deps import role_required
from app.models.maintenance import MaintenanceRequest
from app.schemas.maintenance_schema import MaintenanceCreate, MaintenanceUpdate, MaintenanceOut

router = APIRouter(prefix="/maintenance", tags=["Admin Maintenance"])

@router.post("/requests")
def create_maintenance_request(
    data: MaintenanceCreate,
    hostel_id: int = Query(..., description="Hostel ID"),
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Log a new maintenance request with categorization, priority, photo uploads, cost estimation"""
    # Validate hostel exists
    from app.models.hostel import Hostel
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not hostel:
        raise HTTPException(
            status_code=404,
            detail=f"Hostel with id {hostel_id} not found"
        )
    
    request = MaintenanceRequest(
        hostel_id=hostel_id,
        created_by_id=user.id,
        category=data.category,
        priority=data.priority,
        description=data.description,
        photo_url=data.photo_url,
        est_cost=data.est_cost,
        scheduled_date=data.scheduled_date,
        status="PENDING"
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    return {"id": request.id, "message": "Maintenance request created successfully"}

@router.get("/requests")
def get_maintenance_requests(
    hostel_id: Optional[int] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get maintenance requests with filtering by category, priority, status, assignment"""
    
    query = db.query(MaintenanceRequest)
    
    if hostel_id:
        query = query.filter(MaintenanceRequest.hostel_id == hostel_id)
    if category:
        query = query.filter(MaintenanceRequest.category == category)
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    if assigned_to_id:
        query = query.filter(MaintenanceRequest.assigned_to_id == assigned_to_id)
    
    requests = query.order_by(desc(MaintenanceRequest.created_at)).offset(skip).limit(limit).all()
    
    return {
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
            "completed_date": r.completed_date,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        } for r in requests]
    }

@router.get("/requests/{request_id}")
def get_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get a specific maintenance request by ID"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    return {
        "id": request.id,
        "hostel_id": request.hostel_id,
        "created_by_id": request.created_by_id,
        "category": request.category,
        "priority": request.priority,
        "status": request.status,
        "description": request.description,
        "photo_url": request.photo_url,
        "est_cost": request.est_cost,
        "actual_cost": request.actual_cost,
        "approved": request.approved,
        "assigned_to_id": request.assigned_to_id,
        "scheduled_date": request.scheduled_date,
        "completed_date": request.completed_date,
        "created_at": request.created_at,
        "updated_at": request.updated_at
    }

@router.put("/requests/{request_id}")
def update_maintenance_request(
    request_id: int,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Update maintenance request status, priority, assignment, costs"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    if data.status:
        request.status = data.status
    if data.priority:
        request.priority = data.priority
    if data.description:
        request.description = data.description
    if data.est_cost is not None:
        request.est_cost = data.est_cost
    if data.actual_cost is not None:
        request.actual_cost = data.actual_cost
    if data.assigned_to_id is not None:
        request.assigned_to_id = data.assigned_to_id
    if data.scheduled_date:
        request.scheduled_date = data.scheduled_date
    if data.completed_date:
        request.completed_date = data.completed_date
    
    db.commit()
    return {"ok": True, "message": "Maintenance request updated"}

@router.delete("/requests/{request_id}")
def delete_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Delete a maintenance request"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    db.delete(request)
    db.commit()
    return {"ok": True, "message": "Maintenance request deleted"}

@router.get("/requests/stats/summary")
def get_maintenance_stats(
    hostel_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    """Get maintenance request statistics and analytics"""
    
    query = db.query(MaintenanceRequest)
    if hostel_id:
        query = query.filter(MaintenanceRequest.hostel_id == hostel_id)
    
    total = query.count()
    pending = query.filter(MaintenanceRequest.status == "PENDING").count()
    in_progress = query.filter(MaintenanceRequest.status == "IN_PROGRESS").count()
    completed = query.filter(MaintenanceRequest.status == "COMPLETED").count()
    
    # Category breakdown
    category_stats = db.query(
        MaintenanceRequest.category,
        func.count(MaintenanceRequest.id).label("count")
    ).group_by(MaintenanceRequest.category).all()
    
    # Priority breakdown
    priority_stats = db.query(
        MaintenanceRequest.priority,
        func.count(MaintenanceRequest.id).label("count")
    ).group_by(MaintenanceRequest.priority).all()
    
    return {
        "total_requests": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "category_breakdown": {cat: count for cat, count in category_stats},
        "priority_breakdown": {pri: count for pri, count in priority_stats}
    }
