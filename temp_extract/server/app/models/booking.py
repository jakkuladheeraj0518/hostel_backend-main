from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import BookingStatus


class Booking(BaseEntity):
    """Booking model"""
    __tablename__ = "bookings"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    booking_status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    booking_date = Column(DateTime(timezone=True), nullable=False)
    
    # Booking period
    check_in_date = Column(DateTime(timezone=True), nullable=False)
    check_out_date = Column(DateTime(timezone=True), nullable=True)
    duration_months = Column(Integer, nullable=False, default=1)
    
    # Pricing
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    advance_paid = Column(Float, default=0.0)
    
    # Actual check-in/out
    actual_check_in = Column(DateTime(timezone=True), nullable=True)
    actual_check_out = Column(DateTime(timezone=True), nullable=True)
    
    # Bed assignment
    bed_number = Column(String(50), nullable=True)
    
    # Special requests and notes
    special_requests = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    refund_amount = Column(Float, default=0.0)
    
    # Documents
    documents = Column(Text, nullable=True)  # JSON string of document URLs
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    hostel = relationship("Hostel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, status={self.booking_status})>"