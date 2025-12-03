from typing import List, Optional
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.beds import BedCreate, BedOut, BedUpdate
from app.services.bed_service import (
    create_bed as service_create_bed,
    get_bed as service_get_bed,
    list_beds as service_list_beds,
    list_available_beds as service_list_available_beds,
    update_bed as service_update_bed,
    delete_bed as service_delete_bed,
    assign_bed as service_assign_bed,
    release_bed as service_release_bed,
    transfer_student_bed as service_transfer_student_bed,
    find_bed_by_room_bed as service_find_bed_by_room_bed,
    bulk_assign_beds as bulk_assign_beds_service,
)

# --- RBAC / Permissions imports (new style) ---
from app.models.user import User
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/admin/beds", tags=["beds"])


# ---------------------------------------------------------
# CREATE BED  – SUPERADMIN, ADMIN
# Permission: MANAGE_STUDENTS (or MANAGE_BEDS if you add one)
# ---------------------------------------------------------
@router.post("/", response_model=BedOut, status_code=status.HTTP_201_CREATED)
def create_bed(
    item: BedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        return service_create_bed(db, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# LIST BEDS  – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: READ_HOSTEL
# ---------------------------------------------------------
@router.get("/", response_model=List[BedOut])
def read_beds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return service_list_beds(db, skip=skip, limit=limit)


# ---------------------------------------------------------
# LIST AVAILABLE BEDS – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: READ_HOSTEL
# ---------------------------------------------------------
@router.get("/available", response_model=List[BedOut])
def read_available_beds(
    room_number: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return service_list_available_beds(
        db, room_number=room_number, skip=skip, limit=limit
    )


# ---------------------------------------------------------
# GET BED BY ID – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: READ_HOSTEL
# ---------------------------------------------------------
@router.get("/{bed_id}", response_model=BedOut)
def read_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    bed = service_get_bed(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed


# ---------------------------------------------------------
# UPDATE BED – SUPERADMIN, ADMIN
# Permission: MANAGE_STUDENTS
# ---------------------------------------------------------
@router.put("/{bed_id}", response_model=BedOut)
def update_bed(
    bed_id: int,
    payload: BedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    updated = service_update_bed(db, bed_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


# ---------------------------------------------------------
# DELETE BED – SUPERADMIN, ADMIN
# Permission: MANAGE_STUDENTS
# ---------------------------------------------------------
@router.delete("/{bed_id}", status_code=status.HTTP_200_OK)
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    ok = service_delete_bed(db, bed_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bed not found")
    return JSONResponse(content={"detail": "Bed deleted successfully"})


# ---------------------------------------------------------
# ASSIGN BED TO STUDENT – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: MANAGE_STUDENTS
# ---------------------------------------------------------
@router.post("/{bed_id}/assign", response_model=BedOut)
def assign_bed(
    bed_id: int,
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        updated = service_assign_bed(db, bed_id, student_id)
    except ValueError as e:
        # e.g. bed not available / student already has a bed / not found
        raise HTTPException(status_code=409, detail=str(e))

    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


# ---------------------------------------------------------
# RELEASE BED – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: MANAGE_STUDENTS
# ---------------------------------------------------------
@router.post("/{bed_id}/release", response_model=BedOut)
def release_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        updated = service_release_bed(db, bed_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


# ---------------------------------------------------------
# TRANSFER STUDENT TO NEW BED – SUPERADMIN, ADMIN, SUPERVISOR
# Permission: MANAGE_STUDENTS
# ---------------------------------------------------------
@router.post("/transfer", response_model=BedOut)
def transfer_bed(
    student_id: str,
    new_bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        updated = service_transfer_student_bed(db, student_id, new_bed_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if not updated:
        raise HTTPException(
            status_code=404, detail="Transfer failed or bed not found"
        )
    return updated


# ---------------------------------------------------------
# BULK ASSIGN BEDS (CSV) – SUPERADMIN, ADMIN
# Permission: MANAGE_STUDENTS
# CSV columns: student_id, room_number, bed_number
# ---------------------------------------------------------
@router.post("/bulk/assign")
async def bulk_assign_beds(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))

    assignments = []
    for row in reader:
        assignments.append(
            {
                "student_id": row.get("student_id"),
                "room_number": row.get("room_number"),
                "bed_number": row.get("bed_number"),
            }
        )

    result = bulk_assign_beds_service(db, assignments)
    return result
