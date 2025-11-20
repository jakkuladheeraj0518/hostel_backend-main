from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    recipient_id: str
    recipient_type: str
    channel: str
    subject: Optional[str] = None
    body: Optional[str] = None
    template_name: Optional[str] = None
    template_context: Optional[Dict[str, Any]] = None


class NotificationOut(BaseModel):
    id: int
    recipient_id: str
    recipient_type: str
    channel: str
    subject: Optional[str]
    body: Optional[str]
    sent: bool

    class Config:
        orm_mode = True


class TemplateCreate(BaseModel):
    name: str
    channel: str
    subject_template: Optional[str] = None
    body_template: Optional[str] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    channel: str
    subject_template: Optional[str]
    body_template: Optional[str]
    created_at: Optional[datetime]   # ✅ FIXED

    class Config:
        orm_mode = True


class ProviderStatus(BaseModel):
    sendgrid: bool
    twilio: bool
    fcm: bool
