from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.super_admin_schemas import DashboardResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    try:
        data = DashboardService.get_dashboard_and_activities(db)
        return data
    except Exception as e:
        logger.exception('Error fetching dashboard')
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")
