from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.roles import Role
from app.models.leave import LeaveRequest


# Admin Dashboard

router = APIRouter(prefix="/leave", tags=["Admin Leave"])

@router.get("/leave/requests")
def get_leave_requests(hostel_id: Optional[int] = None, status: Optional[str] = None, 
                      skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
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
def update_leave_request_status(request_id: int, status: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") not in [Role.ADMIN, Role.SUPERADMIN]:
        raise HTTPException(403, "Forbidden")
    
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(404, "Leave request not found")
    
    request.status = status
    db.commit()
    return {"ok": True}

# Notice Management


