from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from datetime import datetime
import enum
from app.config import Base

class EmailProvider(str, enum.Enum):
    sendgrid = "sendgrid"
    aws_ses = "aws_ses"

class EmailStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    faild = "failed"
    delivered = "delivered"
    bounced = "bounced"
    opened = "opened"

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    subject = Column(String)
    html_content = Column(Text)
    text_content = Column(Text, nullable=True)
    variables = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String, index=True)
    subject = Column(String)
    template_id = Column(Integer, nullable=True)
    provider = Column(SQLEnum(EmailProvider))
    status = Column(SQLEnum(EmailStatus), default=EmailStatus.pending)
    message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
