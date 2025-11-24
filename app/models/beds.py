from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, Time, func, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.schema import Identity
from sqlalchemy.orm import relationship

from app.config import Base


class BedStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"


class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, Identity(start=1), primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    bed_number = Column(String(50), nullable=False)
    room_number = Column(String(50), nullable=False)
    bed_status = Column(SAEnum(BedStatus, name="bed_status_enum"), nullable=False, default=BedStatus.AVAILABLE)

    monthly_price = Column(Float, nullable=True)
    quarterly_price = Column(Float, nullable=True)
    annual_price = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    hostel = relationship("Hostel", back_populates="beds")
    room = relationship("Room", back_populates="beds")
