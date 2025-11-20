from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import analytics_services as hostel_summary_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/{hostel_id}")
def get_hostel_summary(hostel_id: int, db: Session = Depends(get_db)):
    """
    Fetch occupancy rate and revenue for a given hostel using stored procedure.
    """
    data = hostel_summary_service.fetch_hostel_summary(db, hostel_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this hostel.")
    
    return {
        "hostel_id": hostel_id,
        "summary": data
    }
