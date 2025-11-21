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

router = APIRouter(prefix="/leave", tags=["Admin Leave"])

@router.get("/leave/requests")
def get_leave_requests(hostel_id: Optional[int] = None, status: Optional[str] = None, 
                      skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    query = db.query(LeaveRequest)
    if hostel_id:
        query = query.filter(LeaveRequest.hostel_id == hostel_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    
    requests = query.offset(skip).limit(limit).all()
    return {"requests": [{"id": r.id, "hostel_id": r.hostel_id, "student_id": r.student_id, 
                         "start_date": r.start_date, "end_date": r.end_date, "reason": r.reason, 
                         "status": r.status} for r in requests]}



@router.put("/leave/requests/{request_id}/status")
def update_leave_request_status(request_id: int, status: str, db: Session = Depends(get_db), user=Depends(current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(403, "Forbidden")
    
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Leave request not found")
    
    request.status = status
    db.commit()
    return {"ok": True}

# Notice Management


