from sqlalchemy import Column, String, Boolean, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntityWithIntId
from .enums import UserType


class User(BaseEntityWithIntId):
    """User model"""
    __tablename__ = "users"
    
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.STUDENT)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Student-specific fields (as per drawio)
    student_id = Column(String(100), nullable=True)  # Added from drawio
    hostel_code = Column(String(50), nullable=True)  # Added from drawio
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    room_number = Column(String(50), nullable=True)
    bed_number = Column(String(50), nullable=True)
    check_in_date = Column(Date, nullable=True)
    blood_group = Column(String(10), nullable=True)  # Added from drawio
    guardian_name = Column(String(255), nullable=True)  # Added from drawio
    guardian_phone = Column(String(20), nullable=True)  # Added from drawio
    status = Column(String(50), nullable=True, default="active")  # Added from drawio
    
    # Essential fields only
    password_reset_token = Column(String(255), nullable=True)
    
    # Relationships (only drawio-specified entities)
    hostel = relationship("Hostel", back_populates="users")
    payments = relationship("Payment", back_populates="user")
    complaints = relationship("Complaint", foreign_keys="Complaint.user_id", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    referrals_made = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referred_id", back_populates="referred")
    attendance_records = relationship("Attendance", foreign_keys="Attendance.user_id", back_populates="user")  # Required for Supervisor Attendance Operations
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, type={self.user_type})>"