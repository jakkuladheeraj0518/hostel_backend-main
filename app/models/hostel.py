from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, Time, TIMESTAMP, ForeignKey, Date
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    hostels = relationship("Hostel", back_populates="location")


class Hostel(Base):
    __tablename__ = "hostels"

    # ---------------------------------------------------
    # Primary Details
    # ---------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # Unified name fields
    hostel_name = Column(String(255), nullable=False)     # main name
    name = Column(String(255), nullable=True)             # optional alias

    # Address info
    full_address = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    # ---------------------------------------------------
    # Additional Metadata
    # ---------------------------------------------------
    description = Column(Text, nullable=True)
    hostel_type = Column(String(100), nullable=True)       # type/category
    gender_type = Column(String(50), nullable=True)        # Boys/Girls/Co-ed
    amenities = Column(Text, nullable=True)                # JSON/text list
    rules = Column(Text, nullable=True)

    # Contact Info
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    # Check-in/check-out
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)

    # ---------------------------------------------------
    # Capacity / Stats
    # ---------------------------------------------------
    total_beds = Column(Integer, nullable=True)
    current_occupancy = Column(Integer, nullable=True)
    monthly_revenue = Column(Numeric(12, 2), nullable=True)

    # ---------------------------------------------------
    # Location Relationship
    # ---------------------------------------------------
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # ---------------------------------------------------
    # Visibility & Flags
    # ---------------------------------------------------
    visibility = Column(String(10), default="public", nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    # ---------------------------------------------------
    # Timestamps
    # ---------------------------------------------------
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    # Optional capacity field (merged from concurrent changes)
    capacity = Column(Integer, default=0)
    # ---------------------------------------------------
    # Relationships
    # ---------------------------------------------------
    # Core relationships
    location = relationship("Location", back_populates="hostels")
    rooms = relationship("Room", back_populates="hostel")

    # Admin assignments / mappings
    admin_assignments = relationship(
        "AdminHostelAssignment",
        back_populates="hostel",
        cascade="all, delete-orphan",
    )
    admin_hostel_mappings = relationship("AdminHostelMapping", back_populates="hostel")

    # Financial & occupancy related
    revenues = relationship("Revenue", back_populates="hostel", cascade="all, delete-orphan")
    occupancies = relationship("Occupancy", back_populates="hostel", cascade="all, delete-orphan")
    users = relationship("User", back_populates="hostel")

    # Additional relationships merged from the other branch
    fee_plans = relationship("FeePlan", back_populates="hostel", cascade="all, delete")
    deposits = relationship("SecurityDeposit", back_populates="hostel", cascade="all, delete")
    mess_charges = relationship("MessCharge", back_populates="hostel", cascade="all, delete")
    services = relationship("AdditionalService", back_populates="hostel", cascade="all, delete")

    payments = relationship("Payment", back_populates="hostel", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="hostel")

    reminder_config = relationship(
        "ReminderConfiguration",
        back_populates="hostel",
        uselist=False,
        cascade="all, delete-orphan",
    )
    session_contexts = relationship("SessionContext", back_populates="hostel")
    audit_logs = relationship("AuditLog", back_populates="hostel")
    approval_requests = relationship("ApprovalRequest", back_populates="hostel")


class Revenue(Base):
    __tablename__ = "revenues"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    revenue = Column(Numeric(12,2), nullable=False)
    hostel = relationship("Hostel", back_populates="revenues")

class Occupancy(Base):
    __tablename__ = "occupancies"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    occupancy_rate = Column(Numeric(5,2), nullable=True)
    hostel = relationship("Hostel", back_populates="occupancies")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(200), nullable=False)
    entity_type = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


