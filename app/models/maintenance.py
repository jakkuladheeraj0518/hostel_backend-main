from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer, Boolean, Text, DateTime, Float, func
from datetime import datetime
from app.models import Base

class Complaint(Base):
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(primary_key=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(64))
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    status: Mapped[str] = mapped_column(String(16), default="PENDING")  # PENDING, IN_PROGRESS, RESOLVED, CLOSED
    description: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(64))  # PLUMBING, ELECTRICAL, HVAC, CLEANING, etc.
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    description: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(512))
    est_cost: Mapped[float | None] = mapped_column(Float)
    actual_cost: Mapped[float | None] = mapped_column(Float)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class MaintenanceCost(Base):
    __tablename__ = "maintenance_costs"
    id: Mapped[int] = mapped_column(primary_key=True)
    maintenance_request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id", ondelete="CASCADE"))
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(64))  # LABOR, MATERIALS, EQUIPMENT, VENDOR
    vendor_name: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Float)
    invoice_url: Mapped[str | None] = mapped_column(String(512))
    payment_status: Mapped[str] = mapped_column(String(16), default="PENDING")  # PENDING, PAID, OVERDUE
    payment_method: Mapped[str | None] = mapped_column(String(32))
    paid_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    maintenance_request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id", ondelete="CASCADE"))
    assigned_to_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_title: Mapped[str] = mapped_column(String(200))
    task_description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="ASSIGNED")  # ASSIGNED, IN_PROGRESS, COMPLETED, VERIFIED
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    estimated_hours: Mapped[float | None] = mapped_column(Float)
    actual_hours: Mapped[float | None] = mapped_column(Float)
    quality_rating: Mapped[int | None] = mapped_column(Integer)  # 1-5 rating
    completion_notes: Mapped[str | None] = mapped_column(Text)
    verification_notes: Mapped[str | None] = mapped_column(Text)
    verified_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime)
    started_date: Mapped[datetime | None] = mapped_column(DateTime)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime)
    verified_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
