
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import analytics_services as hostel_summary_service
from app.repositories.hostel_repository import HostelRepository

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/{hostel_id}")
def get_hostel_summary(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.VIEW_ANALYTICS)),
):
    """
    Fetch occupancy rate and revenue for a given hostel using stored procedure.
    """
    # Validate hostel exists
    hostel_repo = HostelRepository(db)
    if not hostel_repo.get_by_id(hostel_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="hostel id not found")

    data = hostel_summary_service.fetch_hostel_summary(db, hostel_id)

    if not data:
        raise HTTPException(status_code=404, detail="No data found for this hostel.")

    return {
        "hostel_id": hostel_id,
        "summary": data
    }
