from sqlalchemy.orm import Session
from app.models.waitlist import Waitlist
from app.schemas.waitlist import WaitlistCreate


class WaitlistRepository:

    @staticmethod
    def add(db: Session, data: WaitlistCreate):
        entry = Waitlist(**data.dict())
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_next(db: Session, hostel_id: int, room_type: str):
        return db.query(Waitlist).filter(
            Waitlist.hostel_id == hostel_id,
            Waitlist.room_type == room_type
        ).order_by(Waitlist.priority.asc()).first()

    @staticmethod
    def remove(db: Session, entry_id: int):
        db.query(Waitlist).filter(Waitlist.id == entry_id).delete()
        db.commit()

    # ⭐ NEW — Get a waitlist entry by ID (required for promote/delete)
    @staticmethod
    def get_by_id(db: Session, entry_id: int):
        return db.query(Waitlist).filter(Waitlist.id == entry_id).first()

    # ⭐ NEW — List all entries (used by admin or scheduler)
    @staticmethod
    def list_all(db: Session, hostel_id: int, room_type: str = None):
        q = db.query(Waitlist).filter(Waitlist.hostel_id == hostel_id)
        if room_type:
            q = q.filter(Waitlist.room_type == room_type)
        return q.order_by(Waitlist.priority.asc(), Waitlist.created_at.asc()).all()

    # ⭐ NEW — Get top priority entry (shortcut)
    @staticmethod
    def get_top(db: Session, hostel_id: int, room_type: str):
        return (
            db.query(Waitlist)
            .filter(
                Waitlist.hostel_id == hostel_id,
                Waitlist.room_type == room_type
            )
            .order_by(Waitlist.priority.asc(), Waitlist.created_at.asc())
            .first()
        )

    # ⭐ NEW — Count entries for priority assignment
    @staticmethod
    def count(db: Session, hostel_id: int, room_type: str):
        return db.query(Waitlist).filter(
            Waitlist.hostel_id == hostel_id,
            Waitlist.room_type == room_type
        ).count()
