from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_db
from app.core.auth import visitor_required    # 🔐 Visitor Authentication

from app.models.waitlist import Waitlist
from app.schemas.waitlist import WaitlistCreate, WaitlistResponse


router = APIRouter(prefix="/visitor/waitlist", tags=["Visitor Waitlist"])


# ---------------------------------------------------------
# Visitor Add to Waitlist
# ---------------------------------------------------------
@router.post("/", response_model=WaitlistResponse, dependencies=[Depends(visitor_required)])
def add_to_waitlist(payload: WaitlistCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(Waitlist)
        .filter(
            Waitlist.hostel_id == payload.hostel_id,
            Waitlist.room_type == payload.room_type,
            Waitlist.visitor_id == payload.visitor_id,
        )
        .first()
    )
    if exists:
        raise HTTPException(400, "You are already in waitlist for this room type")

    top = (
        db.query(Waitlist)
        .filter(
            Waitlist.hostel_id == payload.hostel_id,
            Waitlist.room_type == payload.room_type,
        )
        .order_by(Waitlist.priority.desc())
        .first()
    )

    next_priority = (top.priority + 1) if top else 1

    wl = Waitlist(
        hostel_id=payload.hostel_id,
        room_type=payload.room_type,
        visitor_id=payload.visitor_id,
        priority=next_priority,
        created_at=datetime.utcnow(),
    )

    db.add(wl)
    db.commit()
    db.refresh(wl)
    return wl


# ---------------------------------------------------------
# Visitor Get Their Own Waitlist Entries
# ---------------------------------------------------------
@router.get("/", response_model=list[WaitlistResponse], dependencies=[Depends(visitor_required)])
def my_waitlist(visitor_id: int, db: Session = Depends(get_db)):
    entries = (
        db.query(Waitlist)
        .filter(Waitlist.visitor_id == visitor_id)
        .order_by(Waitlist.priority.asc(), Waitlist.created_at.asc())
        .all()
    )
    return entries
