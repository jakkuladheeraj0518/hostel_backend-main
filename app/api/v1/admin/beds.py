from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import StringIO

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
)

router = APIRouter(prefix="/api/v1/admin/beds", tags=["beds"])


@router.post("/", response_model=BedOut, status_code=status.HTTP_201_CREATED)
def create_bed(item: BedCreate, db: Session = Depends(get_db)):
    try:
        return service_create_bed(db, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[BedOut])
def read_beds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_list_beds(db, skip=skip, limit=limit)


@router.get("/available", response_model=List[BedOut])
def read_available_beds(room_number: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service_list_available_beds(db, room_number=room_number, skip=skip, limit=limit)


@router.get("/{bed_id}", response_model=BedOut)
def read_bed(bed_id: UUID, db: Session = Depends(get_db)):
    bed = service_get_bed(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed


@router.put("/{bed_id}", response_model=BedOut)
def update_bed(bed_id: UUID, payload: BedUpdate, db: Session = Depends(get_db)):
    updated = service_update_bed(db, bed_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


@router.delete("/{bed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bed(bed_id: UUID, db: Session = Depends(get_db)):
    ok = service_delete_bed(db, bed_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bed not found")
    return None


@router.post("/{bed_id}/assign", response_model=BedOut)
def assign_bed(bed_id: int, student_id: str, db: Session = Depends(get_db)):
    updated = service_assign_bed(db, bed_id, student_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


@router.post("/{bed_id}/release", response_model=BedOut)
def release_bed(bed_id: int, db: Session = Depends(get_db)):
    updated = service_release_bed(db, bed_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Bed not found")
    return updated


@router.post("/transfer", response_model=BedOut)
def transfer_bed(student_id: str, new_bed_id: int, db: Session = Depends(get_db)):
    updated = service_transfer_student_bed(db, student_id, new_bed_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Transfer failed or bed not found")
    return updated


@router.post("/bulk/assign")
async def bulk_assign_beds(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
