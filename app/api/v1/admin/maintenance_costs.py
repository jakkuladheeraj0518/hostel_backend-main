from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.roles import Role
from app.api.deps import role_required
from app.models.maintenance import MaintenanceCost


# Admin Dashboard

router = APIRouter(prefix="/maintenance-costs", tags=["Admin Maintenance Costs"])

@router.get("/maintenance/costs")
def get_all_maintenance_costs(
    hostel_id: Optional[int] = None, 
    category: Optional[str] = None,
    payment_status: Optional[str] = None, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db), 
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    
    from app.models.maintenance import MaintenanceCost
    query = db.query(MaintenanceCost)
    
    if hostel_id:
        query = query.filter(MaintenanceCost.hostel_id == hostel_id)
    if category:
        query = query.filter(MaintenanceCost.category == category)
    if payment_status:
        query = query.filter(MaintenanceCost.payment_status == payment_status)
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(MaintenanceCost.created_at >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(MaintenanceCost.created_at <= end)
    
    costs = query.order_by(desc(MaintenanceCost.created_at)).offset(skip).limit(limit).all()
    return {"costs": [{"id": c.id, "maintenance_request_id": c.maintenance_request_id,
                      "hostel_id": c.hostel_id, "category": c.category, "vendor_name": c.vendor_name,
                      "description": c.description, "amount": c.amount, "payment_status": c.payment_status,
                      "payment_method": c.payment_method, "invoice_url": c.invoice_url,
                      "paid_date": c.paid_date, "created_at": c.created_at} for c in costs]}



