# File removed as the locations router is no longer used.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text

router = APIRouter(prefix="/locations", tags=["locations"])

class LocationCreate(BaseModel):
    city: str

class LocationResponse(BaseModel):
    id: int
    city: str
    created_at: Optional[str]

@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    try:
        sql = text("SELECT * FROM insert_location(:city)")
        result = db.execute(sql, {"city": location.city})
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Location not created")
        return LocationResponse(id=row[0], city=row[1], created_at=str(row[2]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text

router = APIRouter(prefix="/locations", tags=["locations"])

class LocationCreate(BaseModel):
    city: str

class LocationResponse(BaseModel):
    id: int
    city: str
    created_at: Optional[str]

@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    try:
        sql = text("SELECT * FROM insert_location(:city)")
        result = db.execute(sql, {"city": location.city})
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Location not created")
        return LocationResponse(id=row[0], city=row[1], created_at=str(row[2]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
