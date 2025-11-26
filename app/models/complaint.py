from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, Boolean, ForeignKey
from datetime import datetime
import enum
from app.core.database import Base
from sqlalchemy.orm import relationship


# ---------------------------------------------------------------------
# ENUM DEFINITIONS
# ---------------------------------------------------------------------
class ComplaintCategory(str, enum.Enum):
    ROOM_MAINTENANCE = "room_maintenance"
    MESS_QUALITY = "mess_quality"
    CLEANLINESS = "cleanliness"
    SECURITY = "security"
    WIFI = "wifi"  # ✅ Added WiFi as a complaint category
    OTHER = "other"


class ComplaintPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ComplaintStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


# ---------------------------------------------------------------------
# MAIN COMPLAINT MODEL
# ---------------------------------------------------------------------
class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ComplaintCategory), nullable=False)
    priority = Column(Enum(ComplaintPriority), default=ComplaintPriority.MEDIUM)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)

    # Foreign keys to related entities
    student_id = Column(String, ForeignKey("students.student_id"), nullable=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, index=True)

    # Student Info (denormalized for backward compatibility)
    student_name = Column(String(255), nullable=True)
    student_email = Column(String(255), nullable=True)
    hostel_name = Column(String(255), nullable=True)
    room_number = Column(String(50), nullable=True)

    # Assignment Info
    assigned_to_name = Column(String(255), nullable=True)
    assigned_to_email = Column(String(255), nullable=True)

    # Cost and escalation info
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    assigned_at = Column(DateTime, nullable=True)
    in_progress_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    sla_deadline = Column(DateTime, nullable=True)

    # Resolution and feedback
    resolution_notes = Column(Text, nullable=True)
    resources_used = Column(Text, nullable=True)
    student_feedback = Column(Text, nullable=True)
    student_rating = Column(Integer, nullable=True)
    is_reopened = Column(Boolean, default=False)
    reopen_reason = Column(Text, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", foreign_keys=[student_id], backref="complaints")
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reported_complaints")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], backref="assigned_complaints")
    hostel = relationship("Hostel", foreign_keys=[hostel_id], backref="complaints")
    room = relationship("Room", foreign_keys=[room_id], backref="complaints")
    attachments = relationship("ComplaintAttachment", back_populates="complaint", cascade="all, delete-orphan")
    notes = relationship("ComplaintNote", back_populates="complaint", cascade="all, delete-orphan")



# ---------------------------------------------------------------------
# ATTACHMENTS MODEL
# ---------------------------------------------------------------------
class ComplaintAttachment(Base):
    __tablename__ = "complaint_attachments"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(String(255), nullable=False)  # email of uploader
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="attachments")


# ---------------------------------------------------------------------
# NOTES MODEL
# ---------------------------------------------------------------------
class ComplaintNote(Base):
    __tablename__ = "complaint_notes"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)
    note = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True)  # Internal or public notes
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="notes")
