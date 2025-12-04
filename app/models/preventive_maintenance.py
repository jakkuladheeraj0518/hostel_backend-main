from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, Date
from datetime import datetime, date
from app.config import Base

class PreventiveMaintenanceSchedule(Base):
    __tablename__ = "preventive_maintenance_schedules"
    id: Mapped[int] = mapped_column(primary_key=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    equipment_type: Mapped[str] = mapped_column(String(64))
    maintenance_type: Mapped[str] = mapped_column(String(64))
    frequency_days: Mapped[int] = mapped_column(Integer)  # How often in days
    last_maintenance: Mapped[Optional[date]] = mapped_column(Date)
    next_due: Mapped[date] = mapped_column(Date, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PreventiveMaintenanceTask(Base):
    __tablename__ = "preventive_maintenance_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("preventive_maintenance_schedules.id", ondelete="CASCADE"))
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    scheduled_date: Mapped[date] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(String(512))
    cost: Mapped[Optional[int]] = mapped_column(Integer)  # Amount in cents
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)