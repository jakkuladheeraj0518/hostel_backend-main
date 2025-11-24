from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, Time,
    TIMESTAMP, ForeignKey, Date
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.students import Student
from app.core.database import Base


# =========================================================
# LOCATION MODEL
# =========================================================
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    hostels = relationship("Hostel", back_populates="location")


# =========================================================
# HOSTEL MODEL (MERGED VERSION)
# =========================================================
class Hostel(Base):
    __tablename__ = "hostels"

    # ---------------------------------------------------
    # Primary Details
    # ---------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # Unified names
    hostel_name = Column(String(255), nullable=False)      # Main name
    name = Column(String(255), nullable=True)              # Optional alias

    # Address info (merged)
    full_address = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    # ---------------------------------------------------
    # Metadata / Details
    # ---------------------------------------------------
    description = Column(Text, nullable=True)
    hostel_type = Column(String(100), nullable=True)
    gender_type = Column(String(50), nullable=True)       # Boys / Girls / Co-ed
    amenities = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)

    # Contact
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    # Check-in/out times
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)

    # ---------------------------------------------------
    # Stats & Capacity
    # ---------------------------------------------------
    total_beds = Column(Integer, nullable=True)
    current_occupancy = Column(Integer, nullable=True)
    monthly_revenue = Column(Numeric(12, 2), nullable=True)

    # Extra merged field
    capacity = Column(Integer, default=0)

    # ---------------------------------------------------
    # Location Link
    # ---------------------------------------------------
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # ---------------------------------------------------
    # Visibility
    # ---------------------------------------------------
    visibility = Column(String(10), default="public", nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    # ---------------------------------------------------
    # Timestamp
    # ---------------------------------------------------
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # ---------------------------------------------------
    # Relationships
    # ---------------------------------------------------
    location = relationship("Location", back_populates="hostels")

    # Rooms (from second model + first model → already matching)
    rooms = relationship("Room", back_populates="hostel")
    beds = relationship("Bed", back_populates="hostel")
    students = relationship("Student", back_populates="hostel")

    # Admin mappings
    admin_assignments = relationship(
        "AdminHostelAssignment",
        back_populates="hostel",
        cascade="all, delete-orphan",
    )
    admin_hostel_mappings = relationship("AdminHostelMapping", back_populates="hostel")

    # Financial data
    revenues = relationship("Revenue", back_populates="hostel", cascade="all, delete-orphan")
    occupancies = relationship("Occupancy", back_populates="hostel", cascade="all, delete-orphan")

    users = relationship("User", back_populates="hostel")

    # Extra relationships
    fee_plans = relationship("FeePlan", back_populates="hostel", cascade="all, delete")
    deposits = relationship("SecurityDeposit", back_populates="hostel", cascade="all, delete")
    mess_charges = relationship("MessCharge", back_populates="hostel", cascade="all, delete")
    services = relationship("AdditionalService", back_populates="hostel", cascade="all, delete")

    payments = relationship("Payment", back_populates="hostel", cascade="all, delete")
    # Separate relationship for subscription/organization payments
    # `organizationPayment.hostel` uses back_populates="organization_payments"
    organization_payments = relationship(
        "organizationPayment",
        back_populates="hostel",
        cascade="all, delete-orphan",
    )
    
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


# =========================================================
# REVENUE MODEL
# =========================================================
class Revenue(Base):
    __tablename__ = "revenues"

    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    revenue = Column(Numeric(12, 2), nullable=False)

    hostel = relationship("Hostel", back_populates="revenues")


# =========================================================
# OCCUPANCY MODEL
# =========================================================
class Occupancy(Base):
    __tablename__ = "occupancies"

    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    occupancy_rate = Column(Numeric(5, 2), nullable=True)

    hostel = relationship("Hostel", back_populates="occupancies")


# =========================================================
# ACTIVITY LOG MODEL
# =========================================================
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(200), nullable=False)
    entity_type = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
