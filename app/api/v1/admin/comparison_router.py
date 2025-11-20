# app/api/v1/comparison_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.comparison import HostelComparisonRequest, HostelComparisonItem
from app.services.comparison_service import compare_hostels as service_compare_hostels

router = APIRouter(prefix="/api/v1/hostels", tags=["hostels"])


@router.post("/compare", response_model=List[HostelComparisonItem])
def compare_hostels(payload: HostelComparisonRequest, db: Session = Depends(get_db)):
    """
    Compare up to N hostels (validated by schema). Returns pricing, amenities, counts.
    Endpoint kept under /api/v1/hostels/compare for backward compatibility.
    """
    return service_compare_hostels(db, payload.hostel_ids)
