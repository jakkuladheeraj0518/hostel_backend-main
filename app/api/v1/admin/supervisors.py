from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
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

# --- RBAC / permissions ---
from app.models.user import User
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/api/v1/admin/supervisors", tags=["supervisors"])


# -------------------------------------------------------------------
# SUPERVISOR CRUD
# -------------------------------------------------------------------

@router.post(
    "/",
    response_model=SupervisorOut,
    status_code=status.HTTP_201_CREATED,
)
def create_supervisor(
    item: SupervisorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_SUPERVISORS)
    ),
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


@router.get("/", response_model=List[SupervisorOut])
def read_supervisors(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(
        permission_required(Permission.READ_SUPERVISORS)
    ),
):
    return service_list_supervisors(
        db,
        skip=skip,
        limit=limit,
        name=name,
        role=role,
        department=department,
    )


# -------------------------------------------------------------------
# ADMIN OVERRIDES  (Admin Override Mechanism)
# -------------------------------------------------------------------

@router.post(
    "/overrides",
    response_model=AdminOverrideOut,
    status_code=status.HTTP_201_CREATED,
)
def create_override(
    payload: AdminOverrideCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/overrides")
def list_overrides(
    skip: int = 0,
    limit: int = 100,
    admin_employee_id: Optional[str] = None,
    target_supervisor_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.VIEW_OVERRIDES)
    ),
):
    """List admin override records (audit trail)."""
    from app.repositories.supervisor_repository import list_admin_overrides

    return list_admin_overrides(
        db,
        skip=skip,
        limit=limit,
        admin_employee_id=admin_employee_id,
        target_supervisor_id=target_supervisor_id,
    )



@router.get("/{employee_id}", response_model=SupervisorOut)
def read_supervisor(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(
        permission_required(Permission.READ_SUPERVISORS)
    ),
):
    sup = service_get_supervisor(db, employee_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return sup


@router.put("/{employee_id}", response_model=SupervisorOut)
def update_supervisor(
    employee_id: str,
    payload: SupervisorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_SUPERVISORS)
    ),
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


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_supervisor(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_SUPERVISORS)
    ),
):
    ok = service_delete_supervisor(db, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Supervisor deleted"},
    )


# -------------------------------------------------------------------
# SUPERVISOR ↔ HOSTEL ASSIGNMENT
# -------------------------------------------------------------------

@router.post(
    "/{employee_id}/assign-hostel",
    status_code=status.HTTP_200_OK,
)
def assign_hostel(
    employee_id: str,
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_SUPERVISORS)
    ),
):
    service_assign_supervisor_hostel(db, employee_id, hostel_id)
    return JSONResponse(
        content={"detail": "Supervisor assigned to hostel successfully"}
    )


@router.get("/{employee_id}/hostels")
def list_hostels(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(
        permission_required(Permission.READ_SUPERVISORS)
    ),
):
    return service_list_supervisor_hostels(db, employee_id)


# -------------------------------------------------------------------
# SUPERVISOR ACTIVITY (monitoring)
# -------------------------------------------------------------------

@router.get("/{employee_id}/activity")
def activity(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.READ_SUPERVISOR_ACTIVITY)
    ),
):
    return service_list_supervisor_activity(db, employee_id)


# -------------------------------------------------------------------
# ADMIN OVERRIDES  (Admin Override Mechanism)
# -------------------------------------------------------------------

@router.post(
    "/overrides",
    response_model=AdminOverrideOut,
    status_code=status.HTTP_201_CREATED,
)
def create_override(
    payload: AdminOverrideCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    try:
        return service_create_admin_override(
            db,
            payload.admin_employee_id,
            payload.target_supervisor_id,
            payload.action,
            payload.details,
            payload.dict().get("old_state"),
            payload.dict().get("new_state"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/overrides")
def list_overrides(
    skip: int = 0,
    limit: int = 100,
    admin_employee_id: Optional[str] = None,
    target_supervisor_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.VIEW_OVERRIDES)
    ),
):
    """List admin override records (audit trail)."""
    from app.repositories.supervisor_repository import list_admin_overrides

    return list_admin_overrides(
        db,
        skip=skip,
        limit=limit,
        admin_employee_id=admin_employee_id,
        target_supervisor_id=target_supervisor_id,
    )


@router.post(
    "/{employee_id}/override/assign-hostel",
    status_code=status.HTTP_200_OK,
)
def override_assign_hostel(
    employee_id: str,
    new_hostel_id: int,
    admin_employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    