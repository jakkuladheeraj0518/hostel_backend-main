# # app/repositories/announcement_repository.py
# from typing import Optional, List
# from sqlmodel import Session, select
# from app.models.announcement import Announcement, AnnouncementStatus

# class AnnouncementRepository:
#     def __init__(self, session: Session):
#         self.session = session

#     def create(self, announcement: Announcement) -> Announcement:
#         self.session.add(announcement)
#         self.session.commit()
#         self.session.refresh(announcement)
#         return announcement

#     def get(self, announcement_id: int) -> Optional[Announcement]:
#         return self.session.get(Announcement, announcement_id)

#     def update(self, announcement: Announcement) -> Announcement:
#         self.session.add(announcement)
#         self.session.commit()
#         self.session.refresh(announcement)
#         return announcement

#     def delete(self, announcement: Announcement) -> None:
#         self.session.delete(announcement)
#         self.session.commit()

#     def list_all(self, limit: int = 100, offset: int = 0) -> List[Announcement]:
#         stmt = select(Announcement).order_by(Announcement.created_at.desc()).offset(offset).limit(limit)
#         return list(self.session.execute(stmt).scalars())

#     def list_published(self, limit: int = 100, offset: int = 0) -> List[Announcement]:
#         stmt = select(Announcement).where(Announcement.status == AnnouncementStatus.PUBLISHED).order_by(Announcement.created_at.desc()).offset(offset).limit(limit)
#         return list(self.session.execute(stmt).scalars())

#     def list_scheduled_due(self):
#         from datetime import datetime
#         stmt = select(Announcement).where(Announcement.status == AnnouncementStatus.SCHEDULED, Announcement.scheduled_date <= datetime.utcnow())
#         return list(self.session.execute(stmt).scalars())
# app/repositories/announcement_repository.py
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.models.announcement import Announcement, AnnouncementStatus
 
 
class AnnouncementRepository:
    def __init__(self, session: Session):
        self.session = session
 
    def _ensure_sequence(self) -> None:
        """Ensure Postgres sequence for announcement.id is at least MAX(id).
 
        This fixes situations where rows were bulk-inserted or restored and
        the sequence wasn't advanced, causing duplicate key errors on insert.
        """
        try:
            stmt = text(
                "SELECT setval(pg_get_serial_sequence('announcement','id'), (SELECT COALESCE(MAX(id), 1) FROM announcement))"
            )
            # execute within the session - this will update the sequence value
            self.session.execute(stmt)
            # flush the change to ensure DB sees it before next insert
            self.session.commit()
        except Exception:
            # If sequence fix fails for any reason, rollback to keep session usable
            try:
                self.session.rollback()
            except Exception:
                pass
 
    def create(self, announcement: Announcement) -> Announcement:
        self.session.add(announcement)
        try:
            self.session.commit()
        except IntegrityError:
            # Attempt to fix sequence desync and retry once
            self.session.rollback()
            self._ensure_sequence()
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