from datetime import datetime
from enum import Enum

from sqlalchemy import (
	Column,
	Integer,
	String,
	Text,
	DateTime,
	ForeignKey,
	Boolean,
)
from sqlalchemy.orm import relationship

from app.config import Base


class Channel(Enum):
	EMAIL = "email"
	SMS = "sms"
	PUSH = "push"


class Notification(Base):
	__tablename__ = "notifications"

	id = Column(Integer, primary_key=True, index=True)
	recipient_id = Column(String(128), index=True, nullable=False)
	recipient_type = Column(String(64), index=True, nullable=False)  # admin/supervisor/student
	channel = Column(String(32), nullable=False)
	subject = Column(String(255), nullable=True)
	body = Column(Text, nullable=True)
	template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
	sent = Column(Boolean, default=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	sent_at = Column(DateTime, nullable=True)

	attempts = relationship("DeliveryAttempt", back_populates="notification")


class NotificationTemplate(Base):
	__tablename__ = "notification_templates"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(128), unique=True, index=True, nullable=False)
	channel = Column(String(32), nullable=False)
	subject_template = Column(String(255), nullable=True)
	body_template = Column(Text, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)


class DeliveryAttempt(Base):
	__tablename__ = "notification_attempts"

	id = Column(Integer, primary_key=True, index=True)
	notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
	provider = Column(String(64), nullable=True)
	provider_response = Column(Text, nullable=True)
	success = Column(Boolean, default=False)
	attempted_at = Column(DateTime, default=datetime.utcnow)

	notification = relationship("Notification", back_populates="attempts")


class DeviceToken(Base):
	__tablename__ = "device_tokens"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(String(128), index=True, nullable=False)
	platform = Column(String(32), nullable=True)
	token = Column(String(512), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
