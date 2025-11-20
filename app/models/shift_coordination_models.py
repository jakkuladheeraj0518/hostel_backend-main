from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, Date, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    start_time = Column(String(10))
    end_time = Column(String(10))
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    schedules = relationship("ShiftSchedule", back_populates="shift")


class ShiftSchedule(Base):
    __tablename__ = "shift_schedules"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    scheduled_date = Column(Date, nullable=False)
    status = Column(String(20), default="scheduled")
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admin = relationship("Admin")
    shift = relationship("Shift", back_populates="schedules")
    handovers_from = relationship("ShiftHandover", foreign_keys="[ShiftHandover.from_schedule_id]", back_populates="from_schedule")
    handovers_to = relationship("ShiftHandover", foreign_keys="[ShiftHandover.to_schedule_id]", back_populates="to_schedule")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    assigned_to = Column(Integer, ForeignKey("admins.id"))
    assigned_by = Column(Integer, ForeignKey("admins.id"))
    category = Column(String(50))
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship("Admin", foreign_keys=[assigned_to])
    assigner = relationship("Admin", foreign_keys=[assigned_by])
    delegations = relationship("TaskDelegation", back_populates="task")
    updates = relationship("TaskUpdate", back_populates="task")


class TaskDelegation(Base):
    __tablename__ = "task_delegations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    from_admin_id = Column(Integer, ForeignKey("admins.id"))
    to_admin_id = Column(Integer, ForeignKey("admins.id"))
    reason = Column(Text)
    delegated_at = Column(DateTime, default=datetime.utcnow)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="delegations")


class TaskUpdate(Base):
    __tablename__ = "task_updates"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    admin_id = Column(Integer, ForeignKey("admins.id"))
    update_type = Column(String(50))
    old_value = Column(Text)
    new_value = Column(Text)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="updates")


class ShiftHandover(Base):
    __tablename__ = "shift_handovers"

    id = Column(Integer, primary_key=True, index=True)
    from_schedule_id = Column(Integer, ForeignKey("shift_schedules.id"))
    to_schedule_id = Column(Integer, ForeignKey("shift_schedules.id"))
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    handover_time = Column(DateTime, default=datetime.utcnow)
    occupancy_status = Column(Text)
    pending_checkouts = Column(Integer, default=0)
    expected_checkins = Column(Integer, default=0)
    urgent_issues = Column(Text)
    maintenance_required = Column(Text)
    guest_concerns = Column(Text)
    pending_tasks = Column(Text)
    completed_tasks = Column(Text)
    inventory_status = Column(Text)
    cash_handover = Column(DECIMAL(10, 2), nullable=True)
    keys_status = Column(Text)
    notes = Column(Text)
    special_instructions = Column(Text)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledgment_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    from_schedule = relationship("ShiftSchedule", foreign_keys=[from_schedule_id], back_populates="handovers_from")
    to_schedule = relationship("ShiftSchedule", foreign_keys=[to_schedule_id], back_populates="handovers_to")
    items = relationship("HandoverItem", back_populates="handover")


class HandoverItem(Base):
    __tablename__ = "handover_items"

    id = Column(Integer, primary_key=True, index=True)
    handover_id = Column(Integer, ForeignKey("shift_handovers.id"))
    item_type = Column(String(50))
    title = Column(String(255))
    description = Column(Text)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    handover = relationship("ShiftHandover", back_populates="items")


class SupervisorCoordination(Base):
    __tablename__ = "supervisor_coordination"

    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    coordination_date = Column(Date, nullable=False)
    meeting_type = Column(String(50))
    participants = Column(Text)
    agenda = Column(Text)
    discussion_points = Column(Text)
    decisions_made = Column(Text)
    action_items = Column(Text)
    next_meeting = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("admins.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
