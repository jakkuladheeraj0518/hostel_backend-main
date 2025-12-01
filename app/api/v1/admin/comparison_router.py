from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
    get_current_active_user,
    get_repository_context,
    get_user_hostel_ids,
)
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
 
from app.schemas.supervisors import (
    SupervisorCreate,
    SupervisorOut,
    SupervisorUpdate,
    AdminOverrideCreate,
    AdminOverrideOut,
)
from app.services.supervisor_service import (
    create_supervisor as service_create_supervisor,
    get_supervisor as service_get_supervisor,
    list_supervisors as service_list_supervisors,
    update_supervisor as service_update_supervisor,
    delete_supervisor as service_delete_supervisor,
    assign_supervisor_hostel as service_assign_supervisor_hostel,
    list_supervisor_hostels as service_list_supervisor_hostels,
    list_supervisor_activity as service_list_supervisor_activity,
    create_admin_override as service_create_admin_override,
    override_assign_supervisor_hostel as service_override_assign_supervisor_hostel,
)
 
router = APIRouter(prefix="/api/v1/admin/supervisors", tags=["supervisors"])
 
 
# -------------------------------------------------
# CREATE SUPERVISOR - SuperAdmin + Admin
# Supervisor Account Management (create)
# -------------------------------------------------
@router.post("/", response_model=SupervisorOut, status_code=status.HTTP_201_CREATED)
def create_supervisor(
    item: SupervisorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    try:
        return service_create_supervisor(db, item)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "supervisor_email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Supervisor with email '{item.supervisor_email}' already exists",
            )
        if "employee_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Supervisor with employee_id '{item.employee_id}' already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A supervisor with this information already exists",
        )
 
 
# -------------------------------------------------
# LIST SUPERVISORS - SuperAdmin + Admin
# Supervisor Account Management (list/search)
# -------------------------------------------------
@router.get("/", response_model=List[SupervisorOut])
def read_supervisors(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    return service_list_supervisors(
        db,
        skip=skip,
        limit=limit,
        name=name,
        role=role,
        department=department,
    )
 
 
# -------------------------------------------------
# GET SUPERVISOR - SuperAdmin + Admin
# Supervisor Account Management (details)
# -------------------------------------------------
@router.get("/{employee_id}", response_model=SupervisorOut)
def read_supervisor(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    sup = service_get_supervisor(db, employee_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return sup
 
 
# -------------------------------------------------
# UPDATE SUPERVISOR - SuperAdmin + Admin
# Supervisor Account Management (update)
# -------------------------------------------------
@router.put("/{employee_id}", response_model=SupervisorOut)
def update_supervisor(
    employee_id: str,
    payload: SupervisorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    try:
        updated = service_update_supervisor(db, employee_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Supervisor not found")
        return updated
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "supervisor_email" in error_msg:
            email = getattr(payload, "supervisor_email", None)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Supervisor with email '{email}' already exists"
                    if email
                    else "A supervisor with this email already exists"
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A supervisor with this information already exists",
        )
 
 
# -------------------------------------------------
# DELETE SUPERVISOR - SuperAdmin + Admin
# Supervisor Account Management (delete)
# -------------------------------------------------
@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_supervisor(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    ok = service_delete_supervisor(db, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Supervisor deleted"},
    )
 
 
# -------------------------------------------------
# ASSIGN SUPERVISOR TO HOSTEL - SuperAdmin + Admin
# Supervisor Account Management (assign to hostels)
# -------------------------------------------------
@router.post("/{employee_id}/assign-hostel", status_code=status.HTTP_200_OK)
def assign_hostel(
    employee_id: str,
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.ASSIGN_SUPERVISOR)),
):
    service_assign_supervisor_hostel(db, employee_id, hostel_id)
    return JSONResponse(
        content={"detail": "Supervisor assigned to hostel successfully"}
    )
 
 
# -------------------------------------------------
# LIST HOSTELS FOR SUPERVISOR - SuperAdmin + Admin
# Supervisor Account Management (view assignments)
# -------------------------------------------------
@router.get("/{employee_id}/hostels")
def list_hostels(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
):
    return service_list_supervisor_hostels(db, employee_id)
 
 
# -------------------------------------------------
# SUPERVISOR ACTIVITY - SuperAdmin + Admin
# Supervisor Account Management (activity monitoring)
# -------------------------------------------------
@router.get("/{employee_id}/activity")
def activity(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.VIEW_SUPERVISOR_PERFORMANCE)),
):
    return service_list_supervisor_activity(db, employee_id)
 
 
# -------------------------------------------------
# ADMIN OVERRIDES
# -------------------------------------------------
 
# Create override record - SuperAdmin + Admin
@router.post("/overrides", response_model=AdminOverrideOut, status_code=status.HTTP_201_CREATED)
def create_override(
    payload: AdminOverrideCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.OVERRIDE_SUPERVISOR)),
):
    try:
        return service_create_admin_override(
            db,
            payload.admin_employee_id,
            payload.target_supervisor_id,
            payload.action,
            payload.details,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
 
 
# Override + reassign hostel - SuperAdmin + Admin
@router.post("/{employee_id}/override/assign-hostel", status_code=status.HTTP_200_OK)
def override_assign_hostel(
    employee_id: str,
    new_hostel_id: int,
    admin_employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.OVERRIDE_SUPERVISOR)),
):
    try:
        service_override_assign_supervisor_hostel(
            db,
            admin_employee_id,
            employee_id,
            new_hostel_id,
        )
        return JSONResponse(
            content={"detail": "Supervisor override assignment successful"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
 
 
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
 
router = APIRouter(prefix="/api/v1/hostels", tags=["hostels"])
 
 
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
 
 