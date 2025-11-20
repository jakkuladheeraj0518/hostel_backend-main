"""
Multi-hostel admin mapping
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdminHostelMapping(Base):
    __tablename__ = "admin_hostel_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("User", back_populates="admin_hostel_mappings")
    hostel = relationship("Hostel", back_populates="admin_hostel_mappings")
    
    # Unique constraint: one admin can only be mapped to a hostel once
    __table_args__ = (UniqueConstraint('admin_id', 'hostel_id', name='unique_admin_hostel'),)

