# app/services/waitlist_service.py

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.waitlist import Waitlist
from app.models.rooms import Room
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.services.booking_lock_service import BookingLockService


class WaitlistService:
    """
    Simple waitlist service:
    - add_to_waitlist: add visitor entry
    - get_for_hostel: list entries for hostel (ordered by priority & created_at)
    - try_promote: attempt to allocate a room and convert top waitlist entry into a booking
    """

    @staticmethod
    def add_to_waitlist(db: Session, hostel_id: int, room_type: str, visitor_id: int, priority: int = 1) -> Waitlist:
        entry = Waitlist(
            hostel_id=hostel_id,
            room_type=room_type,
            visitor_id=visitor_id,
            priority=priority,
            created_at=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_for_hostel(db: Session, hostel_id: int, room_type: str | None = None):
        q = db.query(Waitlist).filter(Waitlist.hostel_id == hostel_id)
        if room_type:
            q = q.filter(Waitlist.room_type == room_type)
        # priority asc (1 = high), then older first
        return q.order_by(Waitlist.priority.asc(), Waitlist.created_at.asc()).all()

    @staticmethod
    def try_promote(db: Session, hostel_id: int, room_type: str | None = None):
        """
        Try to promote the highest-priority waitlist entry into an actual booking.
        Returns (booking, waitlist_entry) on success, or (None, None) on no-op.
        NOTE:
        - Uses SELECT FOR UPDATE on candidate room to avoid races.
        - Finds any room of requested type in the hostel with available_beds > 0.
        - If found, creates a confirmed booking (amount_paid=0) and removes waitlist entry.
        - Payment/notification logic should be added later.
        """

        # fetch first waitlist entry matching criteria
        q = db.query(Waitlist).filter(Waitlist.hostel_id == hostel_id)
        if room_type:
            q = q.filter(Waitlist.room_type == room_type)

        entry = q.order_by(Waitlist.priority.asc(), Waitlist.created_at.asc()).with_for_update().first()
        if not entry:
            return None, None

        # find any room with available_beds > 0 (we will lock the specific room row)
        rooms = db.query(Room).filter(Room.hostel_id == hostel_id, Room.room_type == entry.room_type, Room.available_beds > 0).all()
        if not rooms:
            # no available room now
            return None, entry

        # pick first candidate room and attempt to lock it
        for r in rooms:
            locked_room = BookingLockService.lock_room(db, r.id)
            if not locked_room:
                # if locked by another tx, try next room
                continue

            # double-check available_beds after locking
            if locked_room.available_beds <= 0:
                # release lock by committing/rolling back (we just continue)
                db.rollback()
                continue

            # create booking object (confirmed). If you prefer pending, change status.
            booking = Booking(
                visitor_id=entry.visitor_id,
                hostel_id=entry.hostel_id,
                room_id=locked_room.id,
                check_in=datetime.utcnow(),           # placeholder; system can set proper dates later
                check_out=datetime.utcnow(),          # placeholder; adapt as needed
                amount_paid=0.0,
                status=BookingStatus.confirmed,
                created_at=datetime.utcnow()
            )

            try:
                db.add(booking)

                # decrement available beds
                locked_room.available_beds = locked_room.available_beds - 1

                # delete waitlist entry
                db.delete(entry)

                db.commit()
                db.refresh(booking)
                return booking, entry

            except Exception:
                db.rollback()
                # release lock implicitly and try next room
                continue

        # no room could be locked/used
        return None, entry

    # -----------------------------------------------------------
    # ⭐ NEW — Get a single waitlist entry by ID
    # -----------------------------------------------------------
    @staticmethod
    def get_by_id(db: Session, waitlist_id: int):
        return db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()

    # -----------------------------------------------------------
    # ⭐ NEW — Remove a waitlist entry (used by router)
    # -----------------------------------------------------------
    @staticmethod
    def remove(db: Session, waitlist_id: int):
        wl = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
        if not wl:
            return False
        db.delete(wl)
        db.commit()
        return True

    # -----------------------------------------------------------
    # ⭐ NEW — Reorder waitlist priorities after deletion/promote
    # -----------------------------------------------------------
    @staticmethod
    def reorder_priorities(db: Session, hostel_id: int, room_type: str):
        entries = (
            db.query(Waitlist)
            .filter(Waitlist.hostel_id == hostel_id, Waitlist.room_type == room_type)
            .order_by(Waitlist.priority.asc(), Waitlist.created_at.asc())
            .all()
        )

        new_priority = 1
        for entry in entries:
            entry.priority = new_priority
            new_priority += 1

        db.commit()
        return True

    # -----------------------------------------------------------
    # ⭐ NEW — Admin Manual Promotion Helper
    # -----------------------------------------------------------
    @staticmethod
    def manual_promote(db: Session, entry: Waitlist):
        """
        Router handles promotion logic; service provides shared helper.
        """
        return entry  # simple placeholder, logic is in router

    # -----------------------------------------------------------
    # ⭐ NEW — Auto promotion hook for Booking cancellation
    # -----------------------------------------------------------
    @staticmethod
    def promote_after_cancellation(db: Session, hostel_id: int, room_type: str):
        """
        Called by BookingService.cancel_booking() to immediately fill freed beds.
        """
        booking, entry = WaitlistService.try_promote(db, hostel_id, room_type)
        return booking
