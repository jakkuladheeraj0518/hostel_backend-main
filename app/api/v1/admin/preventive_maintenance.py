from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.deps import current_user
from app.core.rbac import Role
from app.models.hostel import AdminHostel, Hostel
from app.models.user import User
from app.models.review import Review
from app.models.maintenance import Complaint, MaintenanceRequest, MaintenanceCost, MaintenanceTask
from app.models.leave import LeaveRequest
from app.models.notice import Notice
from app.schemas.user_schema import UserCreate, UserOut
from app.schemas.notice_schema import NoticeCreate
from app.schemas.maintenance_schema import MaintenanceCreate, MaintenanceUpdate, MaintenanceCostCreate
from app.schemas.preventive_maintenance_schema import PreventiveMaintenanceScheduleCreate, PreventiveMaintenanceTaskCreate, PreventiveMaintenanceTaskUpdate
from app.models.preventive_maintenance import PreventiveMaintenanceSchedule, PreventiveMaintenanceTask


# Admin Dashboard

router = APIRouter(prefix="/preventive-maintenance", tags=["Admin Preventive Maintenance"])

@router.post("/preventive-maintenance/schedules")
def create_preventive_schedule(schedule_data: PreventiveMaintenanceScheduleCreate, 
                              db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    schedule = PreventiveMaintenanceSchedule(
        hostel_id=schedule_data.hostel_id,
        equipment_type=schedule_data.equipment_type,
        maintenance_type=schedule_data.maintenance_type,
        frequency_days=schedule_data.frequency_days,
        next_due=schedule_data.next_due
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return {"id": schedule.id}



@router.get("/preventive-maintenance/schedules")
def get_preventive_schedules(hostel_id: Optional[int] = None, db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    query = db.query(PreventiveMaintenanceSchedule).filter(PreventiveMaintenanceSchedule.is_active == True)
    if hostel_id:
        query = query.filter(PreventiveMaintenanceSchedule.hostel_id == hostel_id)
    
    schedules = query.all()
    return {"schedules": [{"id": s.id, "hostel_id": s.hostel_id, "equipment_type": s.equipment_type, 
                          "maintenance_type": s.maintenance_type, "frequency_days": s.frequency_days, 
                          "next_due": s.next_due, "last_maintenance": s.last_maintenance} for s in schedules]}



@router.get("/preventive-maintenance/due")
def get_due_preventive_maintenance(days_ahead: int = 7, hostel_id: Optional[int] = None, 
                                  db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    from datetime import date, timedelta
    due_date = date.today() + timedelta(days=days_ahead)
    
    query = db.query(PreventiveMaintenanceSchedule).filter(
        PreventiveMaintenanceSchedule.is_active == True,
        PreventiveMaintenanceSchedule.next_due <= due_date
    )
    if hostel_id:
        query = query.filter(PreventiveMaintenanceSchedule.hostel_id == hostel_id)
    
    due_schedules = query.all()
    return {"due_schedules": [{"id": s.id, "hostel_id": s.hostel_id, "equipment_type": s.equipment_type, 
                              "maintenance_type": s.maintenance_type, "next_due": s.next_due} for s in due_schedules]}



@router.post("/preventive-maintenance/tasks")
def create_preventive_task(task_data: PreventiveMaintenanceTaskCreate, 
                          db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = PreventiveMaintenanceTask(
        schedule_id=task_data.schedule_id,
        assigned_to_id=task_data.assigned_to_id,
        scheduled_date=task_data.scheduled_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id}



@router.put("/preventive-maintenance/tasks/{task_id}")
def update_preventive_task(task_id: int, task_data: PreventiveMaintenanceTaskUpdate, 
                          db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    task = db.query(PreventiveMaintenanceTask).filter(PreventiveMaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    
    task.status = task_data.status
    if task_data.completed_date:
        task.completed_date = task_data.completed_date
    if task_data.notes:
        task.notes = task_data.notes
    if task_data.cost:
        task.cost = task_data.cost
    
    # If task is completed, update the schedule's next due date
    if task_data.status == "COMPLETED" and task_data.completed_date:
        schedule = db.query(PreventiveMaintenanceSchedule).filter(PreventiveMaintenanceSchedule.id == task.schedule_id).first()
        if schedule:
            from datetime import timedelta
            schedule.last_maintenance = task_data.completed_date
            schedule.next_due = task_data.completed_date + timedelta(days=schedule.frequency_days)
    
    db.commit()
    return {"ok": True}

# Analytics and Reports



