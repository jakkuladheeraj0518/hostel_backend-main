from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, func
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.beds import Bed

from app.core.database import Base


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    DORM = "dorm"
    SUITE = "suite"     # Included from earlier version


class MaintenanceStatus(str, Enum):
    OK = "ok"
    NEEDS_MAINTENANCE = "needs_maintenance"
    OUT_OF_SERVICE = "out_of_service"


# ---------------------------------------------------------
# FINAL MERGED ROOM MODEL
# ---------------------------------------------------------
class Room(Base):
    __tablename__ = "rooms"

    # -----------------------------------------------------
    # Primary Key
    # -----------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # -----------------------------------------------------
    # Hostel Link
    # -----------------------------------------------------
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)

    # -----------------------------------------------------
    # Room Basic Details (Merged)
    # -----------------------------------------------------
    room_number = Column(String(50), nullable=True)   # From version 1

    # Enum room type (advanced)
    room_type = Column(
        SAEnum(RoomType, name="room_type_enum"),
        nullable=False,
        default=RoomType.SINGLE
    )

    # Simple string room_type kept as compatibility? ❌ NO  
    # (Your first version is better — so removed duplicate)

    # -----------------------------------------------------
    # Pricing (Merged)
    # -----------------------------------------------------
    monthly_price = Column(Float, nullable=True)
    quarterly_price = Column(Float, nullable=True)
    annual_price = Column(Float, nullable=True)

    # simple price field (version 2)
    price = Column(Float, nullable=True)  # Optional: for nightly or simplified pricing

    # -----------------------------------------------------
    # Capacity & Beds (Merged)
    # -----------------------------------------------------
    room_capacity = Column(Integer, nullable=False, default=1)   # version 1
    total_beds = Column(Integer, nullable=False, default=1)      # version 2
    available_beds = Column(Integer, nullable=False, default=1)
    availability = Column(Integer, nullable=False, default=0)    # version 1 extra

    # -----------------------------------------------------
    # Amenities
    # -----------------------------------------------------
    amenities = Column(String(1000), nullable=True)

    # -----------------------------------------------------
    # Maintenance
    # -----------------------------------------------------
    maintenance_status = Column(
        SAEnum(MaintenanceStatus, name="maintenance_status_enum"),
        nullable=False,
        default=MaintenanceStatus.OK,
    )

    # -----------------------------------------------------
    # Timestamps
    # -----------------------------------------------------
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # -----------------------------------------------------
    # Relationship → Hostel
    # -----------------------------------------------------
    hostel = relationship("Hostel", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")
    bookings = relationship("Booking", back_populates="room")
