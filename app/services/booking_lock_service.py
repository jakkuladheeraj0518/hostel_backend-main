"""
Booking Lock Service - Handles room locking and conflict detection for bookings
"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.rooms import Room
from app.models.booking import Booking, BookingStatus


class BookingLockService:
    """Service for managing booking locks and conflicts"""

    @staticmethod
    def lock_room(db: Session, room_id: int) -> Room | None:
        """
        Get room without pessimistic locking.
        Just verify the room exists.
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        return room

    @staticmethod
    def has_conflict(db: Session, room_id: int, check_in: datetime, check_out: datetime) -> bool:
        """
        Check if there's a booking conflict for the given room and dates.
        Returns True if there's a conflict, False otherwise.
        """
        try:
            conflict = db.query(Booking).filter(
                Booking.room_id == room_id,
                # FIX: Use .value to compare strings in the DB
                Booking.status.in_([BookingStatus.confirmed.value, BookingStatus.pending.value]),
                Booking.check_in < check_out,
                Booking.check_out > check_in
            ).first()

            return conflict is not None

        except Exception as e:
            print(f"Error checking booking conflict: {str(e)}")
            # If there's an error, assume conflict to be safe
            return True

    @staticmethod
    def unlock_room(db: Session, room_id: int):
        """
        Placeholder for explicit unlock logic if needed.
        """
        pass