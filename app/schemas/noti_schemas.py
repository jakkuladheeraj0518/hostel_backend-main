from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
from app.models.noti_models import EmailProvider, EmailStatus

class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: Optional[str] = "[]"

class EmailTemplateResponse(BaseModel):
    id: int
    name: str
    subject: str
    html_content: str
    text_content: Optional[str]
    variables: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SendEmailRequest(BaseModel):
    recipient: EmailStr
    subject: Optional[str] = None
    template_name: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[Dict] = {}
    provider: EmailProvider = EmailProvider.sendgrid

class EmailLogResponse(BaseModel):
    id: int
    recipient: str
    subject: str
    template_id: Optional[int]
    provider: EmailProvider
    status: EmailStatus
    message_id: Optional[str]
    error_message: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
