from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
 
from app.core.database import get_db
 
# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User
 
from app.schemas.super_admin_schemas import SuccessResponse
from sqlalchemy import text
 
router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])
 
 
class LocationCreate(BaseModel):
    city: str
 
 
class LocationUpdate(BaseModel):
    city: Optional[str] = None
 
 
class LocationResponse(BaseModel):
    id: int
    city: str
    created_at: Optional[str]
 
 
@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),
):
    try:
        # Use direct INSERT with RETURNING to avoid depending on a DB function
        sql = text("INSERT INTO locations (city) VALUES (:city) RETURNING id, city, created_at")
        res = db.execute(sql, {"city": payload.city})
        row = res.fetchone()
        if not row:
            db.rollback()
            raise HTTPException(status_code=500, detail="Location not created")
        db.commit()
        return LocationResponse(id=row[0], city=row[1], created_at=str(row[2]))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.get("/", response_model=List[LocationResponse])
def list_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),
):
    rows = db.execute(text("SELECT id, city, created_at FROM locations ORDER BY id DESC")).fetchall()
    return [LocationResponse(id=r[0], city=r[1], created_at=str(r[2])) for r in rows]
 
 
@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),
):
    row = db.execute(text("SELECT id, city, created_at FROM locations WHERE id = :id"), {"id": location_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationResponse(id=row[0], city=row[1], created_at=str(row[2]))
 
 
@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),
):
    # Build update SQL dynamically
    update_fields = {}
    if payload.city is not None:
        update_fields['city'] = payload.city
 
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
 
    try:
        sql = text("""
            UPDATE locations SET city = :city WHERE id = :id RETURNING id, city, created_at
        """)
        res = db.execute(sql, {**update_fields, "id": location_id})
        row = res.fetchone()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Location not found")
        db.commit()
        return LocationResponse(id=row[0], city=row[1], created_at=str(row[2]))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.delete("/{location_id}", response_model=SuccessResponse)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),
):
    try:
        res = db.execute(text("DELETE FROM locations WHERE id = :id RETURNING id"), {"id": location_id})
        row = res.fetchone()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Location not found")
        db.commit()
        return SuccessResponse(message="Location deleted", data={"id": row[0]})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
 
 