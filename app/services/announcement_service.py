# app/services/announcement_service.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session
from app.models.announcement import Announcement, AnnouncementStatus
from app.repositories.announcement_repository import AnnouncementRepository
from fastapi import HTTPException
from fastapi import UploadFile
import os

UPLOAD_DIR = "uploads/notices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnnouncementService:
    def __init__(self, session: Session):
        self.repo = AnnouncementRepository(session)

    # CREATE
    def create_announcement(self, creator: dict, payload: dict) -> Announcement:
        ann = Announcement(**payload, created_by_id=creator["id"])
        # Supervisor-created urgent/hostel-wide -> require approval
        if creator["role"] == "supervisor":
            if ann.is_emergency or (ann.target_audience and "hostel" in ann.target_audience.lower()):
                ann.approved = False
            else:
                ann.approved = True
            # supervisors do not auto-publish unless allowed by policy; keep draft/scheduled
            ann.status = AnnouncementStatus.SCHEDULED if ann.scheduled_date else AnnouncementStatus.DRAFT
        elif creator["role"] == "admin":
            ann.approved = True
            # admin-created: published immediately if no schedule and not draft
            ann.status = AnnouncementStatus.SCHEDULED if ann.scheduled_date else AnnouncementStatus.PUBLISHED
            if ann.status == AnnouncementStatus.PUBLISHED:
                ann.published = True
        else:
            raise HTTPException(status_code=403, detail="Role not permitted to create announcements")
        return self.repo.create(ann)

    # READ
    def get_announcement(self, announcement_id: int) -> Announcement:
        ann = self.repo.get(announcement_id)
        if not ann:
            raise HTTPException(status_code=404, detail="Announcement not found")
        return ann

    # UPDATE (with basic role checks)
    def update_announcement(self, updater: dict, announcement_id: int, changes: dict) -> Announcement:
        ann = self.get_announcement(announcement_id)
        # Only admin or creator (supervisor who created it) can update
        if updater["role"] != "admin" and ann.created_by_id != updater["id"]:
            raise HTTPException(status_code=403, detail="Not allowed to update this announcement")
        for k, v in changes.items():
            if hasattr(ann, k) and v is not None:
                setattr(ann, k, v)
        # If supervisor updated to make it urgent/hostel-wide, reset approval
        if updater["role"] == "supervisor" and (ann.is_emergency or ("hostel" in (ann.target_audience or "").lower())):
            ann.approved = False
            ann.status = AnnouncementStatus.DRAFT if not ann.scheduled_date else AnnouncementStatus.SCHEDULED
        return self.repo.update(ann)

    # DELETE
    def delete_announcement(self, deleter: dict, announcement_id: int) -> None:
        ann = self.get_announcement(announcement_id)
        if deleter["role"] != "admin" and ann.created_by_id != deleter["id"]:
            raise HTTPException(status_code=403, detail="Not allowed to delete this announcement")
        self.repo.delete(ann)

    # APPROVE (admin only)
    def approve_announcement(self, approver: dict, announcement_id: int) -> Announcement:
        if approver["role"] != "admin":
            raise HTTPException(status_code=403, detail="Only admin can approve")
        ann = self.get_announcement(announcement_id)
        ann.approved = True
        ann.approved_by = approver["id"]
        ann.approved_at = datetime.utcnow()
        # If scheduled date is None, publish immediately
        if not ann.scheduled_date:
            ann.status = AnnouncementStatus.PUBLISHED
            ann.published = True
        return self.repo.update(ann)

    # FORCE PUBLISH (admin)
    def force_publish(self, publisher: dict, announcement_id: int) -> Announcement:
        if publisher["role"] != "admin":
            raise HTTPException(status_code=403, detail="Only admin can publish forcibly")
        ann = self.get_announcement(announcement_id)
        ann.status = AnnouncementStatus.PUBLISHED
        ann.published = True
        ann.approved = True
        return self.repo.update(ann)

    # ADD ATTACHMENT
    def add_attachment(self, announcement_id: int, file: UploadFile, actor: dict) -> Announcement:
        ann = self.get_announcement(announcement_id)
        # only admin or creator can attach
        if actor["role"] != "admin" and ann.created_by_id != actor["id"]:
            raise HTTPException(status_code=403, detail="Not allowed to attach file")
        filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(file.file.read())
        ann.attachments = (ann.attachments or []) + [path]
        return self.repo.update(ann)

    # ACKNOWLEDGE / READ RECEIPT
    def acknowledge(self, announcement_id: int, user_id: int) -> Announcement:
        ann = self.get_announcement(announcement_id)
        readers = ann.read_by or []
        if user_id not in readers:
            readers.append(user_id)
            ann.read_by = readers
            return self.repo.update(ann)
        return ann

    # LISTS
    def list_for_admin(self, limit: int = 100, offset: int = 0) -> List[Announcement]:
        return self.repo.list_all(limit=limit, offset=offset)

    def list_for_student(self, student_hostel_ids: List[int], limit: int = 100, offset: int = 0) -> List[Announcement]:
        # Simple strategy: return published announcements. For target filtering you should expand model to include hostel_ids
        anns = self.repo.list_published(limit=limit, offset=offset)
        # If you have structured target audience, filter here. Returning all published for simplicity.
        return anns

    def publish_due_scheduled(self) -> List[Announcement]:
        due = self.repo.list_scheduled_due()
        published = []
        for ann in due:
            if ann.approved:
                ann.status = AnnouncementStatus.PUBLISHED
                ann.published = True
                published.append(self.repo.update(ann))
        return published
