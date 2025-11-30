from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, Enum as SQLEnum, JSON
)
from datetime import datetime
import enum
from app.config import Base


# ============================================================
# ENUMS
# ============================================================

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    hostel_admin = "hostel_admin"
    hostel_supervisor = "hostel_supervisor"
    student = "student"
    visitor = "visitor"

class NotificationType(str, enum.Enum):
    announcement = "announcement"
    payment_reminder = "payment_reminder"
    complaint_update = "complaint_update"
    maintenance_update = "maintenance_update"
    attendance_alert = "attendance_alert"
    booking_update = "booking_update"
    emergency_alert = "emergency_alert"
    mess_menu = "mess_menu"
    leave_approval = "leave_approval"
    fee_collection = "fee_collection"
    supervisor_task = "supervisor_task"
    admin_directive = "admin_directive"

class NotificationPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    read = "read"

class TargetAudience(str, enum.Enum):
    all_hostels = "all_hostels"
    specific_hostel = "specific_hostel"
    specific_rooms = "specific_rooms"
    specific_floors = "specific_floors"
    specific_users = "specific_users"
    all_students = "all_students"
    all_supervisors = "all_supervisors"
    all_admins = "all_admins"


# ============================================================
# MODELS
# ============================================================

class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    user_role = Column(SQLEnum(UserRole))
    hostel_id = Column(Integer, nullable=True)
    device_token = Column(String, unique=True, index=True)
    device_type = Column(String)
    device_name = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    notification_type = Column(SQLEnum(NotificationType))
    title_template = Column(String)
    body_template = Column(Text)
    data_schema = Column(JSON)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.normal)
    sound = Column(String, default="default")
    badge_increment = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_role = Column(SQLEnum(UserRole))
    hostel_id = Column(Integer, nullable=True)
    notification_type = Column(SQLEnum(NotificationType))
    title = Column(String)
    body = Column(Text)
    data = Column(JSON, nullable=True)
    priority = Column(SQLEnum(NotificationPriority))
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.pending)
    fcm_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    created_by_role = Column(SQLEnum(UserRole), nullable=True)


class NotificationBatch(Base):
    __tablename__ = "notification_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String)
    notification_type = Column(SQLEnum(NotificationType))
    target_audience = Column(SQLEnum(TargetAudience))
    hostel_ids = Column(JSON, nullable=True)
    room_numbers = Column(JSON, nullable=True)
    floor_numbers = Column(JSON, nullable=True)
    user_ids = Column(JSON, nullable=True)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    created_by = Column(Integer)
    created_by_role = Column(SQLEnum(UserRole))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    user_role = Column(SQLEnum(UserRole))

    announcement_enabled = Column(Boolean, default=True)
    payment_reminder_enabled = Column(Boolean, default=True)
    complaint_update_enabled = Column(Boolean, default=True)
    maintenance_update_enabled = Column(Boolean, default=True)
    attendance_alert_enabled = Column(Boolean, default=True)
    booking_update_enabled = Column(Boolean, default=True)
    emergency_alert_enabled = Column(Boolean, default=True)
    mess_menu_enabled = Column(Boolean, default=True)
    leave_approval_enabled = Column(Boolean, default=True)

    quiet_hours_start = Column(String, nullable=True)
    quiet_hours_end = Column(String, nullable=True)

    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class HierarchicalRouting(Base):
    __tablename__ = "hierarchical_routing"

    id = Column(Integer, primary_key=True)
    notification_type = Column(SQLEnum(NotificationType))
    source_role = Column(SQLEnum(UserRole))
    requires_admin_approval = Column(Boolean, default=False)
    route_to_admin = Column(Boolean, default=False)
    route_to_supervisor = Column(Boolean, default=False)
    escalation_threshold_hours = Column(Integer, nullable=True)
    priority_override = Column(SQLEnum(NotificationPriority), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
