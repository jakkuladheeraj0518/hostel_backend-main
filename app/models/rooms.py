from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, func
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    DORM = "dorm"
    SUITE = "suite"        # from your earlier file


class MaintenanceStatus(str, Enum):
    OK = "ok"
    NEEDS_MAINTENANCE = "needs_maintenance"
    OUT_OF_SERVICE = "out_of_service"


# ---------------------------------------------------------
# MERGED ROOM MODEL
# ---------------------------------------------------------
class Room(Base):
    __tablename__ = "rooms"

    # -----------------------------------------------------
    # Primary Identifier
    # -----------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # -----------------------------------------------------
    # Foreign Key → Hostel
    # -----------------------------------------------------
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)

    # -----------------------------------------------------
    # Room Details  (merged)
    # -----------------------------------------------------
    room_number = Column(String(50), nullable=True)     # from version 1
    room_type = Column(
        SAEnum(RoomType, name="room_type_enum"),
        nullable=False,
        default=RoomType.SINGLE
    )

    # Unified pricing
    monthly_price = Column(Float, nullable=True)
    quarterly_price = Column(Float, nullable=True)
    annual_price = Column(Float, nullable=True)

    # Unified capacity & bed info
    room_capacity = Column(Integer, nullable=False, default=1)     # version 1
    total_beds = Column(Integer, nullable=False, default=1)        # version 2
    available_beds = Column(Integer, nullable=False, default=1)    # version 2

    # Amenities
    amenities = Column(String(1000), nullable=True)

    # Maintenance
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
