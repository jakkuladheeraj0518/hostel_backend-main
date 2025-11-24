from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


# BookingStatus used by the booking system (repository/services)
class BookingStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    rejected = "rejected"


# A separate enum for the visitor-facing BookingRequest (keeps older naming)
class BookingRequestStatus(enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Completed = "Completed"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    # Removed student_id column as requested

    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)

    amount_paid = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False, default=BookingStatus.pending.value)  # use simple string for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship to room (used by services)
    room = relationship("Room", back_populates="bookings")


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    id_type = Column(String(50), nullable=False)
    id_number = Column(String(50), nullable=False)
    id_document = Column(String(255), nullable=True)
    emergency_contact_name = Column(String(100), nullable=False)
    emergency_contact_number = Column(String(20), nullable=False)
    emergency_contact_relation = Column(String(50), nullable=True)
    special_requirements = Column(Text, nullable=True)
    status = Column(Enum(BookingRequestStatus), default=BookingRequestStatus.Pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("app.models.user.User", back_populates="bookings")
