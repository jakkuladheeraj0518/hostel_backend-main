# app/api/v1/admin/announcement.py

from fastapi import APIRouter, Depends
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
    prefix="/admin/announcements",
    tags=["Admin Announcements"]      # 🔥 Updated Swagger Tag
)

# TEMP placeholder — replace with your real auth dependency later
def get_current_user_admin():
    return {"id": 1, "role": "admin"}


@router.post("/", response_model=AnnouncementRead)
def create_announcement(
    payload: AnnouncementCreate,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    return svc.create_announcement(current_user, payload.dict())


@router.get("/", response_model=List[AnnouncementRead])
def list_announcements(
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    return svc.list_for_admin()


@router.get("/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    return svc.get_announcement(announcement_id)


@router.put("/{announcement_id}", response_model=AnnouncementRead)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    return svc.update_announcement(
        current_user,
        announcement_id,
        payload.dict(exclude_unset=True)
    )


@router.post("/{announcement_id}/approve")
def approve_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    svc.approve_announcement(current_user, announcement_id)
    return {"detail": "Approved"}


@router.post("/{announcement_id}/publish")
def publish_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    svc.force_publish(current_user, announcement_id)
    return {"detail": "Published"}


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    session: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_admin)
):
    svc = AnnouncementService(session)
    svc.delete_announcement(current_user, announcement_id)
    return {"detail": "Deleted"}
