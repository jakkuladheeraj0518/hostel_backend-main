from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.booking import BookingStatus

from app.services.booking_lock_service import BookingLockService
from app.services.refund_service import RefundService
from app.services.waitlist_service import WaitlistService


class BookingService:

    # ---------------------------------------------------------
    # CREATE BOOKING
    # ---------------------------------------------------------
    @staticmethod
    def create_booking(db: Session, data: BookingCreate):

        # 1️⃣ Lock the room row
        locked_room = BookingLockService.lock_room(db, data.room_id)
        
        if not locked_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found or is currently locked by another transaction"
            )

        # 2️⃣ Check double booking safely
        conflict = BookingLockService.has_conflict(
            db=db,
            room_id=data.room_id,
            check_in=data.check_in,
            check_out=data.check_out
        )

        if conflict:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room is already booked for the selected dates"
            )

        # 3️⃣ Create booking
        try:
            booking = BookingRepository.create(db, data)
            db.commit()
            db.refresh(booking)
            return booking
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Booking failed: {str(e)}")

    # ---------------------------------------------------------
    # MODIFY BOOKING (Visitor)
    # ---------------------------------------------------------
    @staticmethod
    def modify_booking(db: Session, booking_id: int, updates: BookingUpdate):
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(404, "Booking not found")

        if booking.status in [BookingStatus.cancelled, BookingStatus.rejected]:
            raise HTTPException(400, "Cannot modify cancelled/rejected booking")

        # If changing room or dates → check overlap
        if updates.room_id or updates.check_in or updates.check_out:

            room_id = updates.room_id or booking.room_id
            check_in = updates.check_in or booking.check_in
            check_out = updates.check_out or booking.check_out

            overlap = BookingRepository.check_overlap(
                db, room_id, check_in, check_out
            )

            if overlap and overlap.id != booking.id:
                raise HTTPException(400, "New dates/room overlap with another booking")

        return BookingRepository.update(db, booking, updates)

    # ---------------------------------------------------------
    # CANCEL BOOKING (Refund + Auto-Promotion)
    # ---------------------------------------------------------
    @staticmethod
    def cancel_booking(db: Session, booking_id: int):
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(404, "Booking not found")

        if booking.status in [BookingStatus.cancelled, BookingStatus.rejected]:
            return booking  # already cancelled

        # ⭐ Calculate refund
        refund_amount = RefundService.calculate_refund(
            check_in=booking.check_in,
            amount_paid=booking.amount_paid or 0.0
        )

        # ⭐ Cancel booking
        booking.status = BookingStatus.cancelled
        db.commit()
        db.refresh(booking)

        # ⭐ Auto promote next waitlist user
        try:
            WaitlistService.promote_after_cancellation(
                db=db,
                hostel_id=booking.hostel_id,
                room_type=booking.room.room_type
            )
        except Exception:
            pass  # Promotion failures should not block cancellation

        # ⭐ Add refund amount into booking object for response schema
        # (only works if your BookingResponse includes refund_amount)
        booking.refund_amount = refund_amount

        return booking  # FULL booking object returned to match response_model

    # ---------------------------------------------------------
    # CONFIRM BOOKING (Admin)
    # ---------------------------------------------------------
    @staticmethod
    def confirm_booking(db: Session, booking_id: int):
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(404, "Booking not found")

        booking.status = BookingStatus.confirmed
        db.commit()
        db.refresh(booking)
        return booking

    # ---------------------------------------------------------
    # GET SINGLE BOOKING
    # ---------------------------------------------------------
    @staticmethod
    def get_booking(db: Session, booking_id: int):
        return BookingRepository.get_by_id(db, booking_id)

    # ---------------------------------------------------------
    # GET CALENDAR (Hostel-wise booking chart)
    # ---------------------------------------------------------
    @staticmethod
    def get_calendar(db: Session, hostel_id: int):
        return BookingRepository.get_calendar(db, hostel_id)

    # ---------------------------------------------------------
    # ADMIN MODIFY BOOKING (Lock + Conflict Check)
    # ---------------------------------------------------------
    @staticmethod
    def admin_modify_booking(db: Session, booking_id: int, updates: BookingUpdate):
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(404, "Booking not found")

        new_room_id = updates.room_id or booking.room_id
        new_check_in = updates.check_in or booking.check_in
        new_check_out = updates.check_out or booking.check_out

        # 1️⃣ Lock target room
        locked_room = BookingLockService.lock_room(db, new_room_id)
        if not locked_room:
            raise HTTPException(409, "Another admin is modifying this room. Try again.")

        # 2️⃣ Check conflict (but ignore self)
        conflict = BookingLockService.has_conflict(
            db=db,
            room_id=new_room_id,
            check_in=new_check_in,
            check_out=new_check_out
        )

        if conflict and conflict.id != booking.id:
            db.rollback()
            raise HTTPException(
                400,
                "New dates or room overlap with another booking"
            )

        # 3️⃣ Apply update safely
        try:
            booking.room_id = new_room_id
            booking.check_in = new_check_in
            booking.check_out = new_check_out

            db.commit()
            db.refresh(booking)
            return booking

        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Admin modification failed: {str(e)}")
