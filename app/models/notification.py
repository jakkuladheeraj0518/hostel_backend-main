import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship, foreign, backref
from sqlalchemy import cast

from app.core.database import Base


class NotificationChannel(str, enum.Enum):
    # keep lowercase canonical names
    email = "email"
    sms = "sms"
    push = "push"

    # Backwards-compatible uppercase aliases used in older scripts
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"


class NotificationPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


# ------------------------------------------------------------------
# TEMPLATE MODEL
# ------------------------------------------------------------------

class NotificationTemplate(Base):
    """
    Reusable templates for email / SMS / push.
    Example: payment reminders, OTP messages, alerts.
    """
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    channel = Column(String, nullable=False)  # email / sms / push
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ✅ One template -> Many notifications
    notifications = relationship("Notification", back_populates="template")


# ------------------------------------------------------------------
# NOTIFICATION MODEL
# ------------------------------------------------------------------

class Notification(Base):
    """
    A single notification (email/SMS/push) to one recipient.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ Hostel relationship (if tied to a hostel)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    # Use backref on the Notification side so 'notifications' is created on
    # Hostel lazily after both classes are registered (avoids import-order issues).
    hostel = relationship("Hostel", backref=backref("notifications", cascade="all, delete-orphan"))

    # Generic recipient storage
    recipient_id = Column(String, index=True, nullable=False)
    recipient_type = Column(String, index=True, nullable=False)
    # super_admin / admin / supervisor / student / visitor / system

    channel = Column(String, nullable=False)  # email / sms / push
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)

    priority = Column(String, default=NotificationPriority.normal.value, nullable=False)
    status = Column(String, default=NotificationStatus.pending.value, nullable=False)

    error_message = Column(Text, nullable=True)
    template_data = Column(JSON, nullable=True)

    provider_message_id = Column(String, nullable=True)
    provider_response = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # ✅ Template relationship
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    template = relationship("NotificationTemplate", back_populates="notifications")

    # ------------------------------------------------------------------
    # ✅ OPTIONAL Relationships (No DB constraint - Powered by recipient_type)
    # ------------------------------------------------------------------

    student = relationship(
        "Student",
        primaryjoin="foreign(Notification.recipient_id)==Student.student_id",
        viewonly=True
    )

    supervisor = relationship(
        "Supervisor",
        # Supervisor primary key is `employee_id` in the supervisors table.
        # Use `employee_id` here because `Supervisor` doesn't define `supervisor_id`.
        primaryjoin="foreign(Notification.recipient_id)==Supervisor.employee_id",
        viewonly=True
    )

    user = relationship(
        "User",
        primaryjoin="foreign(Notification.recipient_id)==cast(User.id, String)",
        viewonly=True
    )


# ------------------------------------------------------------------
# DEVICE TOKENS FOR PUSH NOTIFICATIONS
# ------------------------------------------------------------------

class DevicePlatform(str, enum.Enum):
    android = "android"
    ios = "ios"
    web = "web"


class NotificationDeviceToken(Base):
    """
    Device token storage for push notifications.
    """
    __tablename__ = "notification_device_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Use backref so the User side doesn't need an explicit relationship
    # declaration. This helps avoid mapper initialization order problems.
    user = relationship("User", backref=backref("device_tokens", cascade="all, delete-orphan"))

    device_token = Column(String, unique=True, nullable=False)
    platform = Column(String, nullable=False)  # android/ios/web
    is_active = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# --- Compatibility / convenience aliases ---
# Older scripts expect DeviceToken and Channel names — keep aliases so imports
# like `from app.models.notification import DeviceToken, Channel` continue to work.
DeviceToken = NotificationDeviceToken
Channel = NotificationChannel
