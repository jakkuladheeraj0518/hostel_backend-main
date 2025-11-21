from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import RoomType, MaintenanceStatus


class Room(BaseEntity):
    """Room model - Updated to match drawio requirements"""
    __tablename__ = "rooms"
    
    # Basic room information (as per drawio)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_number = Column(String(50), nullable=False)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    room_capacity = Column(Integer, nullable=False)  # Updated field name as per drawio
    
    # Pricing tiers (as per drawio requirements)
    monthly_price = Column(Float, nullable=False)
    quarterly_price = Column(Float, nullable=False)
    annual_price = Column(Float, nullable=False)
    
    # Availability (as per drawio)
    availability = Column(Integer, nullable=False, default=0)  # Available beds count
    
    # Amenities (as per drawio)
    amenities = Column(String(1000), nullable=True)
    
    # Maintenance status (as per drawio)
    maintenance_status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.GOOD)
    
    # Legacy fields for backward compatibility (minimal set)
    capacity = Column(Integer, nullable=True)
    current_occupancy = Column(Integer, default=0)
    is_occupied = Column(Boolean, default=False)
    price_per_month = Column(Float, nullable=True)
    
    # Relationships
    hostel = relationship("Hostel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
    
    def __repr__(self):
        return f"<Room(id={self.id}, number={self.room_number}, type={self.room_type})>"
    
    @property
    def is_available(self):
        """Check if room has available beds"""
        return self.current_occupancy < self.capacity