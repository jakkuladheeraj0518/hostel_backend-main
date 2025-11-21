from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.rooms import Room
from app.schemas.booking import (
    BookingCreateSchema,
    BookingResponseSchema,
    BookingUpdateSchema,
    BookingStatusUpdateSchema,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ---------------------------------------------------------
# CHECK DOUBLE BOOKING
# ---------------------------------------------------------
def is_room_available(db: Session, room_id: int, check_in: datetime, check_out: datetime):
    return (
        db.query(Booking)
        .filter(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.confirmed,
            Booking.check_in < check_out,
            Booking.check_out > check_in
        )
        .first()
        is None
    )


# ---------------------------------------------------------
# CREATE BOOKING
# ---------------------------------------------------------
@router.post("/", response_model=BookingResponseSchema)
def create_booking(payload: BookingCreateSchema, db: Session = Depends(get_db)):

    room = db.query(Room).filter(Room.id == payload.room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    if room.available_beds <= 0:
        raise HTTPException(400, "No beds available in this room")

    # Prevent overlapping confirmed bookings
    if not is_room_available(db, payload.room_id, payload.check_in, payload.check_out):
        raise HTTPException(400, "Room is not available for these dates")

    booking = Booking(
        hostel_id=payload.hostel_id,
        room_id=payload.room_id,
        visitor_id=payload.visitor_id,
        check_in=payload.check_in,
        check_out=payload.check_out,
        amount_paid=payload.amount_paid,
        status=BookingStatus.pending,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


# ---------------------------------------------------------
# GET ALL BOOKINGS
# ---------------------------------------------------------
@router.get("/", response_model=List[BookingResponseSchema])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()


# ---------------------------------------------------------
# GET SINGLE BOOKING
# ---------------------------------------------------------
@router.get("/{booking_id}", response_model=BookingResponseSchema)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking


# ---------------------------------------------------------
# UPDATE BOOKING DETAILS (DATE, ROOM)
# ---------------------------------------------------------
@router.put("/{booking_id}", response_model=BookingResponseSchema)
def update_booking(booking_id: int, payload: BookingUpdateSchema, db: Session = Depends(get_db)):

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")

    # Changing Room → Check availability first
    if payload.room_id:
        room = db.query(Room).filter(Room.id == payload.room_id).first()
        if not room:
            raise HTTPException(404, "Room not found")

        if not is_room_available(
            db, payload.room_id,
            payload.check_in or booking.check_in,
            payload.check_out or booking.check_out
        ):
            raise HTTPException(400, "New room not available on selected dates")

        booking.room_id = payload.room_id

    # Update dates
    if payload.check_in:
        booking.check_in = payload.check_in
    if payload.check_out:
        booking.check_out = payload.check_out

    db.commit()
    db.refresh(booking)
    return booking


# ---------------------------------------------------------
# UPDATE STATUS (ADMIN)
# ---------------------------------------------------------
@router.patch("/{booking_id}/status", response_model=BookingResponseSchema)
def update_status(booking_id: int, payload: BookingStatusUpdateSchema, db: Session = Depends(get_db)):

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")

    new_status = payload.status

    # When confirming, ensure room has free beds
    if new_status == BookingStatus.confirmed:
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        if room.available_beds <= 0:
            raise HTTPException(400, "No beds available to confirm booking")

        room.available_beds -= 1

    # When canceling → release bed
    if new_status == BookingStatus.cancelled:
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        room.available_beds += 1

    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking
