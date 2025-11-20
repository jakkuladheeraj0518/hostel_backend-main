from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.hostel import Hostel
import enum

class PermissionLevel(str, enum.Enum):
    read = "read"
    write = "write"
    admin = "admin"

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    hostel_assignments = relationship("AdminHostelAssignment", back_populates="admin")

class AdminHostelAssignment(Base):
    __tablename__ = "admin_hostel_assignments"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    permission_level = Column(Enum(PermissionLevel, name='permission_level'), nullable=False, default=PermissionLevel.read)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship("Admin", back_populates="hostel_assignments")
    hostel = relationship("Hostel", back_populates="admin_assignments")
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        UniqueConstraint('admin_id', 'hostel_id', name='uq_admin_hostel_assignment'),
    )