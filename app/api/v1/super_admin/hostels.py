# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from app.core.database import get_db
# from app.schemas.super_admin_schemas import HostelCreate, HostelUpdate, HostelUpsert, HostelResponse, SuccessResponse
# from app.services.super_admin_service import HostelService
# import logging

# logger = logging.getLogger(__name__)
# router = APIRouter(prefix="/api/v1/hostels", tags=["Hostels"])

# @router.post("/", response_model=HostelResponse, status_code=status.HTTP_201_CREATED)
# def create_hostel(payload: HostelCreate, db: Session = Depends(get_db)):
#     upsert_data = HostelUpsert(**payload.model_dump(), id=None)
#     result = HostelService.upsert_hostel(db, upsert_data)
#     if not result:
#         raise HTTPException(status_code=400, detail="Failed to create hostel")
#     return result

# @router.put("/{hostel_id}", response_model=HostelResponse)
# def update_hostel(hostel_id: int, payload: HostelUpdate, db: Session = Depends(get_db)):
#     existing = HostelService.get_hostel_by_id(db, hostel_id)
#     if not existing:
#         raise HTTPException(status_code=404, detail="Hostel not found")
#     update_data = payload.model_dump(exclude_unset=True)
#     merged = {**existing, **update_data}
#     # Ensure we don't pass 'id' twice (merged may already contain 'id')
#     merged.pop('id', None)
#     upsert = HostelUpsert(**merged, id=hostel_id)
#     result = HostelService.upsert_hostel(db, upsert)
#     if not result:
#         raise HTTPException(status_code=400, detail="Failed to update hostel")
#     return result

# @router.get("/", response_model=List[HostelResponse])
# def list_hostels(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), search: Optional[str] = None, db: Session = Depends(get_db)):
#     if search:
#         return HostelService.search_hostels(db, search, skip, limit)
#     return HostelService.get_all_hostels(db, skip, limit)

# @router.get("/{hostel_id}", response_model=HostelResponse)
# def get_hostel(hostel_id: int, db: Session = Depends(get_db)):
#     res = HostelService.get_hostel_by_id(db, hostel_id)
#     if not res:
#         raise HTTPException(status_code=404, detail="Hostel not found")
#     return res

# @router.delete("/{hostel_id}", response_model=SuccessResponse)
# def delete_hostel(hostel_id: int, db: Session = Depends(get_db)):
#     deleted = HostelService.delete_hostel(db, hostel_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Hostel not found")
#     return SuccessResponse(message="Hostel deleted", data={"id": deleted})
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.super_admin_schemas import (
    HostelCreate, HostelUpdate, HostelUpsert,
    HostelResponse, SuccessResponse
)
from app.services.super_admin_service import HostelService

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/hostels", tags=["Hostels"])


# -----------------------------------------------------------
# CREATE HOSTEL  (SuperAdmin Only)
# -----------------------------------------------------------
@router.post("/", response_model=HostelResponse, status_code=status.HTTP_201_CREATED)
def create_hostel(
    payload: HostelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)
),
):
    upsert_data = HostelUpsert(**payload.model_dump(), id=None)
    result = HostelService.upsert_hostel(db, upsert_data)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create hostel")
    return result


# -----------------------------------------------------------
# UPDATE HOSTEL  (SuperAdmin Only)
# -----------------------------------------------------------
@router.put("/{hostel_id}", response_model=HostelResponse)
def update_hostel(
    hostel_id: int,
    payload: HostelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)
),
):
    existing = HostelService.get_hostel_by_id(db, hostel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hostel not found")

    update_data = payload.model_dump(exclude_unset=True)
    merged = {**existing, **update_data}
    merged.pop('id', None)

    upsert = HostelUpsert(**merged, id=hostel_id)
    result = HostelService.upsert_hostel(db, upsert)

    if not result:
        raise HTTPException(status_code=400, detail="Failed to update hostel")
    return result


# -----------------------------------------------------------
# LIST HOSTELS  (Admin + SuperAdmin + Supervisor)
# -----------------------------------------------------------
@router.get("/", response_model=List[HostelResponse])
def list_hostels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)
),
):
    if search:
        return HostelService.search_hostels(db, search, skip, limit)
    return HostelService.get_all_hostels(db, skip, limit)


# -----------------------------------------------------------
# GET HOSTEL DETAILS (Admin + SuperAdmin + Supervisor)
# -----------------------------------------------------------
@router.get("/{hostel_id}", response_model=HostelResponse)
def get_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)
),
):
    res = HostelService.get_hostel_by_id(db, hostel_id)
    if not res:
        raise HTTPException(status_code=404, detail="Hostel not found")
    return res


# -----------------------------------------------------------
# DELETE HOSTEL (SuperAdmin Only)
# -----------------------------------------------------------
@router.delete("/{hostel_id}", response_model=SuccessResponse)
def delete_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)
),
):
    deleted = HostelService.delete_hostel(db, hostel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hostel not found")
    return SuccessResponse(message="Hostel deleted", data={"id": deleted})
