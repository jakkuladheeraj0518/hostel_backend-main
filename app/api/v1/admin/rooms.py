from typing import List, Optional
import csv
from io import StringIO

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Path,
)
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
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

# RBAC imports
from app.models.user import User
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/admin/rooms", tags=["rooms"])


# ---------------------------------------------------------------------
# CREATE ROOM
# ---------------------------------------------------------------------
@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_ROOMS)),
):
    try:
        room = service_create_room(db, payload)
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------
# LIST ROOMS WITH FILTERS
# ---------------------------------------------------------------------
@router.get("/", response_model=List[RoomOut])
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
    _: None = Depends(permission_required(Permission.READ_ROOMS)),
):
    rt = None
    ms = None

    if room_type:
        try:
            rt = RoomType(room_type)
        except ValueError:
            raise HTTPException(400, f"Invalid room_type: {room_type}")

    if maintenance_status:
        try:
            ms = MaintenanceStatus(maintenance_status)
        except ValueError:
            raise HTTPException(400, f"Invalid maintenance_status: {maintenance_status}")

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


# ---------------------------------------------------------------------
# BULK IMPORT ROOMS (must come before /{room_id})
# ---------------------------------------------------------------------
@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_import_rooms(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.IMPORT_ROOMS)),
):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))

    created = 0
    for row in reader:
        try:
            payload = {k: (v if v else None) for k, v in row.items()}
            service_create_room(db, RoomCreate(**payload))
            created += 1
        except Exception:
            continue

    return {"created": created}


# ---------------------------------------------------------------------
# EXPORT ROOMS (must come before /{room_id})
# ---------------------------------------------------------------------
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
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.EXPORT_ROOMS)),
):
    rt = None
    ms = None

    if room_type:
        rt = RoomType(room_type)
    if maintenance_status:
        ms = MaintenanceStatus(maintenance_status)

    rows = service_list_rooms(
        db,
        skip=0,
        limit=999999,
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


# ---------------------------------------------------------------------
# GET SINGLE ROOM
# ---------------------------------------------------------------------
@router.get("/{room_id}", response_model=RoomOut)
def get_room(
    room_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_ROOMS)),
):
    room = service_get_room(db, room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    return room


# ---------------------------------------------------------------------
# UPDATE ROOM
# ---------------------------------------------------------------------
@router.put("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_ROOMS)),
):
    updated = service_update_room(db, room_id, payload)
    if not updated:
        raise HTTPException(404, "Room not found")
    return updated


# ---------------------------------------------------------------------
# DELETE ROOM
# ---------------------------------------------------------------------
@router.delete("/{room_id}", status_code=200)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_ROOMS)),
):
    try:
        ok = service_delete_room(db, room_id)
    except ValueError as e:
        raise HTTPException(409, str(e))

    if not ok:
        raise HTTPException(404, "Room not found")

    return {"detail": "Room deleted successfully"}


# ---------------------------------------------------------------------
# SET MAINTENANCE STATUS
# ---------------------------------------------------------------------
@router.post("/{room_id}/maintenance", response_model=RoomOut)
def set_maintenance(
    room_id: int,
    maintenance_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_ROOMS)),
):
    try:
        ms = MaintenanceStatus(maintenance_status)
    except ValueError:
        raise HTTPException(400, f"Invalid maintenance_status: {maintenance_status}")

    updated = service_set_room_maintenance(db, room_id, ms)
    if not updated:
        raise HTTPException(404, "Room not found")

    return updated


# ---------------------------------------------------------------------
# SET ROOM AVAILABILITY
# ---------------------------------------------------------------------
@router.post("/{room_id}/availability", response_model=RoomOut)
def set_availability(
    room_id: int,
    availability: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_ROOMS)),
):
    updated = service_set_room_availability(db, room_id, availability)
    if not updated:
        raise HTTPException(404, "Room not found")

    return updated