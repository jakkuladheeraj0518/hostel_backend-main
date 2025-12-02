import enum

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    hostel_admin = "hostel_admin"
    hostel_supervisor = "hostel_supervisor"
    student = "student"
    visitor = "visitor"

class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"
    in_app = "in_app"


class NotificationCategory(str, enum.Enum):
    complaint = "complaint"
    maintenance = "maintenance"
    attendance = "attendance"
    payment = "payment"
    booking = "booking"
    announcement = "announcement"
    emergency = "emergency"
    leave_request = "leave_request"
    mess_menu = "mess_menu"
    room_allocation = "room_allocation"
    security = "security"
    fee_reminder = "fee_reminder"
    otp = "otp"
    welcome = "welcome"
    supervisor_task = "supervisor_task"
    admin_directive = "admin_directive"


class NotificationPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"
    critical = "critical"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    partially_sent = "partially_sent"
    failed = "failed"
    delivered = "delivered"
    read = "read"

class FallbackStrategy(str, enum.Enum):
    none = "none"
    sms_if_email_fails = "sms_if_email_fails"
    push_if_email_fails = "push_if_email_fails"
    all_channels = "all_channels"
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum as SQLEnum
from datetime import datetime
from app.config import Base

class NotificationTemplate(Base):
    __tablename__ = "unified_notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(SQLEnum(NotificationCategory))

    email_subject = Column(String, nullable=True)
    email_template = Column(Text, nullable=True)
    sms_template = Column(Text, nullable=True)
    push_title = Column(String, nullable=True)
    push_body = Column(Text, nullable=True)
    in_app_template = Column(Text, nullable=True)

    enabled_channels = Column(JSON)
    primary_channel = Column(SQLEnum(NotificationChannel))
    fallback_strategy = Column(SQLEnum(FallbackStrategy))

    variables = Column(JSON)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.normal)
    requires_routing = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UnifiedNotificationLog(Base):
    __tablename__ = "unified_notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_module = Column(String)
    source_reference_id = Column(Integer, nullable=True)
    template_id = Column(Integer, nullable=True)

    user_id = Column(Integer, index=True)
    user_role = Column(SQLEnum(UserRole))
    hostel_id = Column(Integer, nullable=True)

    recipient_email = Column(String, nullable=True)
    recipient_phone = Column(String, nullable=True)

    category = Column(SQLEnum(NotificationCategory))
    priority = Column(SQLEnum(NotificationPriority))

    title = Column(String)
    message = Column(Text)
    data = Column(JSON)

    channels_attempted = Column(JSON)
    email_status = Column(String, nullable=True)
    sms_status = Column(String, nullable=True)
    push_status = Column(String, nullable=True)

    status = Column(SQLEnum(NotificationStatus))
    fallback_executed = Column(Boolean, default=False)
    fallback_channel = Column(SQLEnum(NotificationChannel), nullable=True)

    routed = Column(Boolean, default=False)
    routing_log_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class UserChannelPreference(Base):
    __tablename__ = "user_channel_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    user_role = Column(SQLEnum(UserRole))

    complaint_channels = Column(JSON, default=["email", "push"])
    maintenance_channels = Column(JSON, default=["email", "push"])
    attendance_channels = Column(JSON, default=["email", "sms", "push"])
    payment_channels = Column(JSON, default=["email", "sms", "push"])
    booking_channels = Column(JSON, default=["email", "sms", "push"])
    announcement_channels = Column(JSON, default=["push"])
    emergency_channels = Column(JSON, default=["email", "sms", "push"])

    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)

    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String, nullable=True)
    quiet_hours_end = Column(String, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationBatch(Base):
    __tablename__ = "unified_notification_batches"

    id = Column(Integer, primary_key=True)
    batch_name = Column(String)
    category = Column(SQLEnum(NotificationCategory))

    total_recipients = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    email_sent = Column(Integer, default=0)
    sms_sent = Column(Integer, default=0)
    push_sent = Column(Integer, default=0)

    status = Column(String, default="pending")
    created_by = Column(Integer)
    created_by_role = Column(SQLEnum(UserRole))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
