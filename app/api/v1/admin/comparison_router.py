
 
# app/api/v1/comparison_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.schemas.comparison import HostelComparisonRequest, HostelComparisonItem
from app.services.comparison_service import compare_hostels as service_compare_hostels
 
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
    get_current_active_user,
    get_repository_context,
    get_user_hostel_ids,
)
from app.models.user import User
 
router = APIRouter(prefix="/hostels", tags=["hostels"])
 
 
@router.get("/compare", response_model=List[HostelComparisonItem])
def compare_hostels(
    hostel_ids: List[int] = Query(..., description="List of hostel IDs to compare"),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT,
            Role.VISITOR,
        ])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    """
    Compare up to N hostels (validated by schema).
    Returns pricing, amenities, counts.
 
    Permissions:
    - Roles: SUPERADMIN, ADMIN, SUPERVISOR, STUDENT, VISITOR
    - Permission: READ_HOSTEL (view hostel details/comparison)
 
    Endpoint kept under /api/v1/hostels/compare for backward compatibility.
    """
    # validate & normalize using pydantic schema (enforces non-empty and max 4)
    req = HostelComparisonRequest(hostel_ids=hostel_ids)
    return service_compare_hostels(db, req.hostel_ids)
 
 