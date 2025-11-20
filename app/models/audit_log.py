"""
🧾 Audit logs for supervisor/admin actions
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g., "GET", "POST", "PUT", "DELETE"
    resource = Column(String, nullable=False)  # e.g., "/api/v1/users"
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(Text, nullable=True)  # JSON string for additional details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    hostel = relationship("Hostel", back_populates="audit_logs")

