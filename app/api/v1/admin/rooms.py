from typing import List, Optional
from uuid import UUID  # Unused, kept for reference
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Path
from fastapi.responses import StreamingResponse, JSONResponse
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
 
from app.schemas.rooms import RoomCreate, RoomOut, RoomUpdate
from app.services.room_service import (
    create_room as service_create_room,
    get_room as service_get_room,
    list_rooms as service_list_rooms,
    update_room as service_update_room,
    delete_room as service_delete_room,
    set_room_maintenance as service_set_room_maintenance,
    set_room_availability as service_set_room_availability,
)
from app.models.rooms import RoomType, MaintenanceStatus
 
router = APIRouter(prefix="/admin/rooms", tags=["rooms"])
 
 
# -------------------------------------------------
# CREATE ROOM - Hostel Admin + Super Admin
# -------------------------------------------------
@router.post(
    "/",
    response_model=RoomOut,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    item: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    try:
        # TODO: if needed, restrict by current_user hostel_ids here
        room = service_create_room(db, item)
        room.hostel_id = str(room.hostel_id)  # Ensure hostel_id is returned as a string
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# -------------------------------------------------
# LIST ROOMS - Admin + Supervisor + Super Admin
# -------------------------------------------------
@router.get(
    "/",
    response_model=List[RoomOut],
)
def read_rooms(
    skip: int = 0,
    limit: int = 100,
    room_type: Optional[str] = None,
    maintenance_status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_capacity: Optional[int] = None,
    only_available: Optional[bool] = None,
    amenities_like: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    rt = None
    ms = None
    if room_type:
        try:
            rt = RoomType(room_type)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid room_type: {room_type}")
    if maintenance_status:
        try:
            ms = MaintenanceStatus(maintenance_status)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid maintenance_status: {maintenance_status}")
 
    # Optional: filter by hostel_ids based on current_user + SOW
    # hostel_ids = get_user_hostel_ids(current_user)
    # return service_list_rooms(db, ..., hostel_ids=hostel_ids)
 
    return service_list_rooms(
        db,
        skip=skip,
        limit=limit,
        room_type=rt,
        maintenance_status=ms,
        min_price=min_price,
        max_price=max_price,
        min_capacity=min_capacity,
        only_available=only_available,
        amenities_like=amenities_like,
    )
 
 
# -------------------------------------------------
# EXPORT ROOMS - Admin + Supervisor + Super Admin
# -------------------------------------------------
@router.get("/export")
def export_rooms(
    room_type: Optional[str] = None,
    maintenance_status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_capacity: Optional[int] = None,
    only_available: Optional[bool] = None,
    amenities_like: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    rt = None
    ms = None
    if room_type:
        try:
            rt = RoomType(room_type)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid room_type: {room_type}")
    if maintenance_status:
        try:
            ms = MaintenanceStatus(maintenance_status)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid maintenance_status: {maintenance_status}")

    rows = service_list_rooms(
        db,
        skip=0,
        limit=100000,
        room_type=rt,
        maintenance_status=ms,
        min_price=min_price,
        max_price=max_price,
        min_capacity=min_capacity,
        only_available=only_available,
        amenities_like=amenities_like,
    )

    buf = StringIO()
    writer = csv.writer(buf)
    headers = [
        "id",
        "hostel_id",
        "room_number",
        "room_type",
        "room_capacity",
        "monthly_price",
        "quarterly_price",
        "annual_price",
        "availability",
        "amenities",
        "maintenance_status",
        "created_at",
        "updated_at",
    ]
    writer.writerow(headers)
    for r in rows:
        writer.writerow([getattr(r, h, None) for h in headers])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rooms.csv"},
    )
 
 
# -------------------------------------------------
# UPDATE ROOM - Hostel Admin + Super Admin
# -------------------------------------------------
@router.put(
    "/{room_id}",
    response_model=RoomOut,
)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    updated = service_update_room(db, room_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    if hasattr(updated, "hostel_id"):
        updated.hostel_id = str(updated.hostel_id)
    return updated
 
 
# -------------------------------------------------
# DELETE ROOM - Hostel Admin + Super Admin
# -------------------------------------------------
@router.delete(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    ok = service_delete_room(db, room_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Room not found")
    return JSONResponse(content={"detail": "Room deleted successfully"})
 
 
# -------------------------------------------------
# SET MAINTENANCE STATUS - Supervisor + Hostel Admin + Super Admin
# -------------------------------------------------
@router.post(
    "/{room_id}/maintenance",
    response_model=RoomOut,
)
def set_maintenance(
    room_id: int,
    maintenance_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_MAINTENANCE)),
):
    try:
        ms = MaintenanceStatus(maintenance_status)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid maintenance_status: {maintenance_status}")
    updated = service_set_room_maintenance(db, room_id, ms)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    if hasattr(updated, "hostel_id"):
        updated.hostel_id = str(updated.hostel_id)
    return updated
 
 
# -------------------------------------------------
# SET AVAILABILITY - Supervisor + Hostel Admin + Super Admin
# -------------------------------------------------
@router.post(
    "/{room_id}/availability",
    response_model=RoomOut,
)
def set_availability(
    room_id: int,
    availability: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_MAINTENANCE)),
):
    updated = service_set_room_availability(db, room_id, availability)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    if hasattr(updated, "hostel_id"):
        updated.hostel_id = str(updated.hostel_id)
    return updated
 
 
# -------------------------------------------------
# BULK IMPORT ROOMS - Hostel Admin + Super Admin
# -------------------------------------------------
@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
)
async def bulk_import_rooms(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ROOM_TYPES)),
):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    created = 0
    for row in reader:
        try:
            payload = {k: (v if v != "" else None) for k, v in row.items()}
            service_create_room(db, RoomCreate(**payload))
            created += 1
        except Exception:
            continue
    return {"created": created}
 
 
# -------------------------------------------------
# EXPORT ROOMS - Admin + Supervisor + Super Admin
# -------------------------------------------------
@router.get("/export")
def export_rooms(
    room_type: Optional[str] = None,
    maintenance_status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_capacity: Optional[int] = None,
    only_available: Optional[bool] = None,
    amenities_like: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    rt = None
    ms = None
    if room_type:
        try:
            rt = RoomType(room_type)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid room_type: {room_type}")
    if maintenance_status:
        try:
            ms = MaintenanceStatus(maintenance_status)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid maintenance_status: {maintenance_status}")
 
    rows = service_list_rooms(
        db,
        skip=0,
        limit=100000,
        room_type=rt,
        maintenance_status=ms,
        min_price=min_price,
        max_price=max_price,
        min_capacity=min_capacity,
        only_available=only_available,
        amenities_like=amenities_like,
    )
 
    buf = StringIO()
    writer = csv.writer(buf)
    headers = [
        "id",
        "hostel_id",
        "room_number",
        "room_type",
        "room_capacity",
        "monthly_price",
        "quarterly_price",
        "annual_price",
        "availability",
        "amenities",
        "maintenance_status",
        "created_at",
        "updated_at",
    ]
    writer.writerow(headers)
    for r in rows:
        writer.writerow([getattr(r, h, None) for h in headers])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rooms.csv"},
    )