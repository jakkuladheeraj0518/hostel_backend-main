"""
Admin Maintenance Task Assignment
Assign tasks to staff/vendors, track progress, completion verification, quality checks
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.roles import Role
from app.models.maintenance import MaintenanceTask, MaintenanceRequest
from app.schemas.maintenance_schema import MaintenanceTaskCreate, MaintenanceTaskUpdate, MaintenanceTaskOut

router = APIRouter(prefix="/maintenance/tasks", tags=["Admin Maintenance Tasks"])

@router.post("")
def create_maintenance_task(
    data: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Assign maintenance task to staff or vendor with tracking"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    # Verify maintenance request exists
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == data.maintenance_request_id
    ).first()
    if not request:
        raise HTTPException(404, "Maintenance request not found")
    
    task = MaintenanceTask(
        maintenance_request_id=data.maintenance_request_id,
        assigned_to_id=data.assigned_to_id,
        task_title=data.task_title,
        task_description=data.task_description,
        priority=data.priority,
        estimated_hours=data.estimated_hours,
        scheduled_date=data.scheduled_date,
        status="ASSIGNED"
    )
    
    db.add(task)
    
    # Update maintenance request assignment
    request.assigned_to_id = data.assigned_to_id
    request.status = "IN_PROGRESS"
    
    db.commit()
    db.refresh(task)
    
    return {
        "id": task.id,
        "message": "Task assigned successfully",
        "assigned_to_id": task.assigned_to_id
    }

@router.get("")
def get_maintenance_tasks(
    maintenance_request_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get maintenance tasks with filtering"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    query = db.query(MaintenanceTask)
    
    if maintenance_request_id:
        query = query.filter(MaintenanceTask.maintenance_request_id == maintenance_request_id)
    if assigned_to_id:
        query = query.filter(MaintenanceTask.assigned_to_id == assigned_to_id)
    if status:
        query = query.filter(MaintenanceTask.status == status)
    if priority:
        query = query.filter(MaintenanceTask.priority == priority)
    
    tasks = query.order_by(desc(MaintenanceTask.created_at)).offset(skip).limit(limit).all()
    
    return {
        "tasks": [{
            "id": t.id,
            "maintenance_request_id": t.maintenance_request_id,
            "assigned_to_id": t.assigned_to_id,
            "task_title": t.task_title,
            "task_description": t.task_description,
            "status": t.status,
            "priority": t.priority,
            "estimated_hours": t.estimated_hours,
            "actual_hours": t.actual_hours,
            "quality_rating": t.quality_rating,
            "completion_notes": t.completion_notes,
            "verification_notes": t.verification_notes,
            "verified_by_id": t.verified_by_id,
            "scheduled_date": t.scheduled_date,
            "started_date": t.started_date,
            "completed_date": t.completed_date,
            "verified_date": t.verified_date,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        } for t in tasks]
    }

@router.get("/{task_id}")
def get_maintenance_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get specific maintenance task details"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    return {
        "id": task.id,
        "maintenance_request_id": task.maintenance_request_id,
        "assigned_to_id": task.assigned_to_id,
        "task_title": task.task_title,
        "task_description": task.task_description,
        "status": task.status,
        "priority": task.priority,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "quality_rating": task.quality_rating,
        "completion_notes": task.completion_notes,
        "verification_notes": task.verification_notes,
        "verified_by_id": task.verified_by_id,
        "scheduled_date": task.scheduled_date,
        "started_date": task.started_date,
        "completed_date": task.completed_date,
        "verified_date": task.verified_date,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

@router.put("/{task_id}/progress")
def update_task_progress(
    task_id: int,
    data: MaintenanceTaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Update task progress, status, and completion details"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    if data.status:
        task.status = data.status
        if data.status == "IN_PROGRESS" and not task.started_date:
            task.started_date = datetime.now()
        elif data.status == "COMPLETED" and not task.completed_date:
            task.completed_date = datetime.now()
    
    if data.actual_hours is not None:
        task.actual_hours = data.actual_hours
    if data.completion_notes:
        task.completion_notes = data.completion_notes
    if data.started_date:
        task.started_date = data.started_date
    if data.completed_date:
        task.completed_date = data.completed_date
    
    db.commit()
    return {"ok": True, "message": "Task progress updated"}

@router.put("/{task_id}/verify")
def verify_task_completion(
    task_id: int,
    quality_rating: int = Query(..., ge=1, le=5, description="Quality rating 1-5"),
    verification_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Verify task completion with quality check"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    if task.status != "COMPLETED":
        raise HTTPException(400, "Task must be completed before verification")
    
    task.status = "VERIFIED"
    task.quality_rating = quality_rating
    task.verification_notes = verification_notes
    task.verified_by_id = user.get("id")
    task.verified_date = datetime.now()
    
    # Update maintenance request status
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == task.maintenance_request_id
    ).first()
    if request:
        request.status = "COMPLETED"
        request.completed_date = datetime.now()
    
    db.commit()
    return {
        "ok": True,
        "message": "Task verified successfully",
        "quality_rating": quality_rating
    }

@router.put("/{task_id}/reassign")
def reassign_task(
    task_id: int,
    new_assigned_to_id: int = Query(..., description="New staff/vendor ID"),
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Reassign task to different staff or vendor"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    old_assigned_to = task.assigned_to_id
    task.assigned_to_id = new_assigned_to_id
    task.status = "ASSIGNED"  # Reset to assigned status
    
    # Update maintenance request assignment
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == task.maintenance_request_id
    ).first()
    if request:
        request.assigned_to_id = new_assigned_to_id
    
    db.commit()
    return {
        "ok": True,
        "message": "Task reassigned successfully",
        "old_assigned_to_id": old_assigned_to,
        "new_assigned_to_id": new_assigned_to_id
    }

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Delete a maintenance task"""
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    db.delete(task)
    db.commit()
    return {"ok": True, "message": "Task deleted"}
