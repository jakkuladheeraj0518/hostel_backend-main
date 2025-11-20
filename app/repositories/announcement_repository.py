# app/repositories/announcement_repository.py
from typing import Optional, List
from sqlmodel import Session, select
from app.models.announcement import Announcement, AnnouncementStatus

class AnnouncementRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, announcement: Announcement) -> Announcement:
        self.session.add(announcement)
        self.session.commit()
        self.session.refresh(announcement)
        return announcement

    def get(self, announcement_id: int) -> Optional[Announcement]:
        return self.session.get(Announcement, announcement_id)

    def update(self, announcement: Announcement) -> Announcement:
        self.session.add(announcement)
        self.session.commit()
        self.session.refresh(announcement)
        return announcement

    def delete(self, announcement: Announcement) -> None:
        self.session.delete(announcement)
        self.session.commit()

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Announcement]:
        stmt = select(Announcement).order_by(Announcement.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars())

    def list_published(self, limit: int = 100, offset: int = 0) -> List[Announcement]:
        stmt = select(Announcement).where(Announcement.status == AnnouncementStatus.PUBLISHED).order_by(Announcement.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars())

    def list_scheduled_due(self):
        from datetime import datetime
        stmt = select(Announcement).where(Announcement.status == AnnouncementStatus.SCHEDULED, Announcement.scheduled_date <= datetime.utcnow())
        return list(self.session.execute(stmt).scalars())
