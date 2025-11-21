from sqlalchemy import Column, String, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import BedStatus


class Bed(BaseEntity):
    """Bed model for individual bed management"""
    __tablename__ = "beds"
    
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_number = Column(String(50), nullable=False)
    bed_number = Column(String(50), nullable=False)
    bed_status = Column(SQLEnum(BedStatus), nullable=False, default=BedStatus.AVAILABLE)
    
    # Pricing tiers (as per drawio requirements)
    monthly_price = Column(Float, nullable=False)
    quarterly_price = Column(Float, nullable=False)
    annual_price = Column(Float, nullable=False)
    
    # Current occupant
    current_occupant_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    
    # Bed details
    bed_type = Column(String(50), nullable=True)  # single, bunk_top, bunk_bottom
    has_mattress = Column(String(1), default='Y')  # Y/N
    has_pillow = Column(String(1), default='Y')   # Y/N
    has_blanket = Column(String(1), default='Y')  # Y/N
    
    # Maintenance
    last_cleaned = Column(String, nullable=True)
    maintenance_notes = Column(String(500), nullable=True)
    
    # Relationships
    hostel = relationship("Hostel", back_populates="beds")
    current_occupant = relationship("User", foreign_keys=[current_occupant_id])
    
    def __repr__(self):
        return f"<Bed(id={self.id}, room={self.room_number}, bed={self.bed_number}, status={self.bed_status})>"
    
    @property
    def is_available(self):
        """Check if bed is available for booking"""
        return self.bed_status == BedStatus.AVAILABLE and self.current_occupant_id is None