from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import csv
from io import StringIO
 
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
)
 
router = APIRouter(prefix="/admin/beds", tags=["beds"])
 
 
# -------------------------------------------------
# CREATE BED - Hostel Admin + Super Admin
# Bed structure management (CRUD)
# -------------------------------------------------
@router.post("/", response_model=BedOut, status_code=status.HTTP_201_CREATED)
def create_bed(
    item: BedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    try:
        return service_create_bed(db, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# -------------------------------------------------
# LIST BEDS - Admin + Supervisor + Super Admin
# Bed inventory view
# -------------------------------------------------
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
 
 
# -------------------------------------------------
# LIST AVAILABLE BEDS - Admin + Supervisor + Super Admin
# Bed availability tracking
# -------------------------------------------------
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
        db,
        room_number=room_number,
        skip=skip,
        limit=limit,
    )
 
 
# -------------------------------------------------
# GET BED - Admin + Supervisor + Super Admin
# Bed detail
# -------------------------------------------------
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
    if hasattr(bed, "hostel_id"):
        bed.hostel_id = str(bed.hostel_id) if bed.hostel_id is not None else None
    return bed
 
 
# -------------------------------------------------
# UPDATE BED - Hostel Admin + Super Admin
# Bed structure management (update)
# -------------------------------------------------
@router.put("/{bed_id}", response_model=BedOut)
def update_bed(
    bed_id: int,
    payload: BedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    updated = service_update_bed(db, bed_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    if hasattr(updated, "hostel_id"):
        updated.hostel_id = str(updated.hostel_id) if updated.hostel_id is not None else None
    return updated
 
 
# -------------------------------------------------
# DELETE BED - Hostel Admin + Super Admin
# Bed structure management (delete)
# -------------------------------------------------
@router.delete("/{bed_id}", status_code=status.HTTP_200_OK)
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    ok = service_delete_bed(db, bed_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bed not found")
    return JSONResponse(content={"detail": "Bed deleted successfully"})
 
 
# -------------------------------------------------
# ASSIGN BED - Hostel Admin + Super Admin
# Bed Allocation APIs (assign to student/booking)
# -------------------------------------------------
@router.post("/{bed_id}/assign", response_model=BedOut)
def assign_bed(
    bed_id: int,
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = service_assign_bed(db, bed_id, student_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated
 
 
# -------------------------------------------------
# RELEASE BED - Hostel Admin + Super Admin
# Bed Allocation APIs (release)
# -------------------------------------------------
@router.post("/{bed_id}/release", response_model=BedOut)
def release_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = service_release_bed(db, bed_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated
 
 
# -------------------------------------------------
# TRANSFER STUDENT BED - Hostel Admin + Super Admin
# Bed Allocation APIs (transfer management)
# -------------------------------------------------
@router.post("/transfer", response_model=BedOut)
def transfer_bed(
    student_id: str,
    new_bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    updated = service_transfer_student_bed(db, student_id, new_bed_id)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Transfer failed or bed not found",
        )
    return updated
 
 
# -------------------------------------------------
# BULK ASSIGN BEDS - Hostel Admin + Super Admin
# Bed Allocation APIs (bulk operations)
# -------------------------------------------------
@router.post("/bulk/assign")
async def bulk_assign_beds(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    assigned = 0
    skipped = 0
 
    for row in reader:
        student_id = row.get("student_id")
        room_number = row.get("room_number")
        bed_number = row.get("bed_number")
 
        if not student_id or not room_number or not bed_number:
            skipped += 1
            continue
 
        bed = service_find_bed_by_room_bed(db, room_number, bed_number)
        if not bed:
            skipped += 1
            continue
 
        try:
            service_assign_bed(db, bed.id, student_id)
            assigned += 1
        except Exception:
            skipped += 1
            continue
 
    return {"assigned": assigned, "skipped": skipped}
 