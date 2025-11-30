from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, Float
from datetime import datetime
import enum
from app.config import Base
from sqlalchemy import JSON

class SMSProvider(str, enum.Enum):
    twilio = "twilio"
    aws_sns = "aws_sns"

class SMSStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    undelivered = "undelivered"

class MessageType(str, enum.Enum):
    otp = "otp"
    payment_reminder = "payment_reminder"
    emergency_alert = "emergency_alert"
    promotional = "promotional"
    transactional = "transactional"

class OTPStatus(str, enum.Enum):
    active = "active"
    verified = "verified"
    expired = "expired"
    failed = "failed"

class SMSTemplate(Base):
    __tablename__ = "sms_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    message_type = Column(SQLEnum(MessageType))
    content = Column(Text)
    variables = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SMSLog(Base):
    __tablename__ = "sms_logs"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    message = Column(Text)
    message_type = Column(SQLEnum(MessageType))
    template_id = Column(Integer, nullable=True)
    provider = Column(SQLEnum(SMSProvider))
    status = Column(SQLEnum(SMSStatus), default=SMSStatus.pending)
    message_sid = Column(String, nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class OTPS(Base):
    __tablename__ = "otpss"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    otp_code = Column(String)
    otp_hash = Column(String, index=True)
    purpose = Column(String)
    status = Column(SQLEnum(OTPStatus), default=OTPStatus.active)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    sms_log_id = Column(Integer, nullable=True)
    expires_at = Column(DateTime, index=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PaymentReminders(Base):
    __tablename__ = "payment_reminderss"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    customer_name = Column(String)
    amount = Column(Float)
    due_date = Column(DateTime)
    invoice_number = Column(String, unique=True, index=True)
    reminder_sent = Column(Boolean, default=False)
    sms_log_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)
    severity = Column(String)
    target_groups = Column(Text)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime, nullable=True)
