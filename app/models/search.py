from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    STUDENT = "student"

class AdminHostelMapping(Base):
    __tablename__ = "admin_hostel_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(255))
    user_role = Column(Enum(UserRole), nullable=False)
    hostel_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)