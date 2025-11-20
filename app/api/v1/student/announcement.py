# app/api/v1/student/announcement.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.announcement import AnnouncementRead
from app.core.database import get_db
from app.services.announcement_service import AnnouncementService

router = APIRouter(
    prefix="/student/announcements",
    tags=["Student Announcements"]      # 🔥 Updated Swagger Tag
)

# TEMP placeholder — replace with real user auth logic later
def get_current_student():
    return {"id": 501, "role": "student", "hostel_ids": [1]}


@router.get("/", response_model=List[AnnouncementRead])
def list_announcements(
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_student)
):
    svc = AnnouncementService(session)
    return svc.list_for_student(current_user["hostel_ids"])


@router.get("/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_student)
):
    svc = AnnouncementService(session)
    return svc.get_announcement(announcement_id)


@router.post("/{announcement_id}/acknowledge")
def acknowledge(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_student)
):
    svc = AnnouncementService(session)
    svc.acknowledge(announcement_id, current_user["id"])
    return {"detail": "Acknowledged"}
