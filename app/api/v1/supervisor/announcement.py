# app/api/v1/supervisor/announcement.py

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementRead,
    AnnouncementUpdate
)
from app.core.database import get_db
from app.services.announcement_service import AnnouncementService

router = APIRouter(
    prefix="/supervisor/announcements",
    tags=["Supervisor Announcements"]      # 🔥 Role-specific Swagger tag
)

# TEMP placeholder — replace with your real supervisor auth dependency
def get_current_user():
    return {"id": 101, "role": "supervisor"}


@router.post("/", response_model=AnnouncementRead)
def create_announcement(
    payload: AnnouncementCreate,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    svc = AnnouncementService(session)
    return svc.create_announcement(current_user, payload.dict())


@router.put("/{announcement_id}", response_model=AnnouncementRead)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    svc = AnnouncementService(session)
    return svc.update_announcement(
        current_user,
        announcement_id,
        payload.dict(exclude_unset=True)
    )


@router.post("/{announcement_id}/attach", response_model=AnnouncementRead)
def attach_file(
    announcement_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    svc = AnnouncementService(session)
    return svc.add_attachment(announcement_id, file, current_user)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    svc = AnnouncementService(session)
    svc.delete_announcement(current_user, announcement_id)
    return {"detail": "Deleted"}
