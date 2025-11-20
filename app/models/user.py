"""
👤 User model with role & hostel_id
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base
from app.core.roles import Role


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    # `phone_number` stores the user's phone number (preferably in E.164 format, e.g. +911234567890)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    country_code = Column(String, nullable=True)  # Country code (e.g., +1, +91)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for social login
    full_name = Column(String, nullable=True)
    role = Column(String, default=Role.VISITOR.value, nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    is_active = Column(Boolean, default=False)  # Default False until OTP verified
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)  # Profile picture URL
    # Removed social OAuth columns (social login was disabled/removed)
    remember_me = Column(Boolean, default=False)  # For extended session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hostel = relationship("Hostel", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    admin_hostel_mappings = relationship("AdminHostelMapping", back_populates="admin")
    session_contexts = relationship("SessionContext", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")

    