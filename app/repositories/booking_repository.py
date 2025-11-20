from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingRepository:

    @staticmethod
    def create(db: Session, data: BookingCreate) -> Booking:
        booking = Booking(
            visitor_id=data.visitor_id,
            hostel_id=data.hostel_id,
            room_id=data.room_id,
            check_in=data.check_in,
            check_out=data.check_out,

            # ⭐ REQUIRED FIELDS ADDED
            amount_paid=data.amount_paid,        # <-- required
            status="pending"                     # <-- required
        )
        db.add(booking)

        # ⭐ REQUIRED COMMIT + REFRESH (must be here)
        db.commit()
        db.refresh(booking)

        return booking

    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Booking | None:
        return db.query(Booking).filter(Booking.id == booking_id).first()

    # ✅ REQUIRED: Overlapping date check
    @staticmethod
    def check_overlap(db: Session, room_id: int, check_in, check_out) -> Booking | None:
        """
        Returns a booking if there is an overlap.
        Used in modify booking (not in create booking anymore).
        """
        return (
            db.query(Booking)
            .filter(
                Booking.room_id == room_id,
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .first()
        )

    @staticmethod
    def update(db: Session, booking: Booking, updates: BookingUpdate):
        """
        Update booking with partial fields.
        """
        if updates.check_in is not None:
            booking.check_in = updates.check_in

        if updates.check_out is not None:
            booking.check_out = updates.check_out

        if updates.room_id is not None:
            booking.room_id = updates.room_id

        db.commit()
        db.refresh(booking)
        return booking

    # Optional: used in calendar API
    @staticmethod
    def get_calendar(db: Session, hostel_id: int):
        return (
            db.query(Booking)
            .filter(Booking.hostel_id == hostel_id)
            .all()
        )
