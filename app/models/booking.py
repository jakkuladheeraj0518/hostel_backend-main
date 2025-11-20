from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    rejected = "rejected"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, nullable=False)

    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)

    amount_paid = Column(Float, default=0)

    # ⭐ IMPORTANT FIX — prevent SQLAlchemy from auto-creating ENUM
    status = Column(
        Enum(BookingStatus, name="bookingstatus", create_type=False),
        server_default="pending",
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room")
