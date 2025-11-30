"""
👤 User model with role & hostel_id
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.core.roles import Role


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    country_code = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default=Role.VISITOR.value, nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    is_active = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)
    remember_me = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    name = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    hostel = relationship("Hostel", back_populates="users")
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    admin_hostel_mappings = relationship("AdminHostelMapping", back_populates="admin")
    session_contexts = relationship("SessionContext", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    
    # FIX: Use full string path "app.models.booking.BookingRequest"
    bookings = relationship("app.models.booking.BookingRequest", back_populates="user")
    supervisor = relationship("User", remote_side=[id], foreign_keys=[supervisor_id])
    admin = relationship("User", remote_side=[id], foreign_keys=[admin_id])
    student = relationship("Student", back_populates="user", uselist=False)
    supervisor_data = relationship("Supervisor", back_populates="user", uselist=False)

    admin_data = relationship("Admin", back_populates="user", uselist=False)  
    
class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)