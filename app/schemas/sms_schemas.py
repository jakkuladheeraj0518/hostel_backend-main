from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.sms_models import (
    MessageType,
    SMSProvider,
    SMSStatus,
    OTPStatus
)


# ============================================================
# TEMPLATE SCHEMAS
# ============================================================

class SMSTemplateCreate(BaseModel):
    name: str
    message_type: MessageType
    content: str
    variables: Optional[List[str]] = []   # FIXED: list instead of string


class SMSTemplateResponse(BaseModel):
    id: int
    name: str
    message_type: MessageType
    content: str
    variables:List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# SEND SMS
# ============================================================

class SendSMSRequest(BaseModel):
    phone_number: str
    message: Optional[str] = None
    template_name: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None   # FIXED: no mutable default
    message_type: MessageType = MessageType.transactional
    provider: SMSProvider = SMSProvider.twilio


# ============================================================
# OTP
# ============================================================

class SendOTPRequest(BaseModel):
    phone_number: str
    purpose: str = "verification"
    otp_length: int = 6
    validity_minutes: int = 10
    provider: SMSProvider = SMSProvider.twilio


class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str
    purpose: str = "verification"


class OTPResponse(BaseModel):
    id: int
    phone_number: str
    purpose: str
    status: OTPStatus
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PAYMENT REMINDERS
# ============================================================

class PaymentReminderCreate(BaseModel):
    phone_number: str
    customer_name: str
    amount: float
    due_date: datetime
    invoice_number: str


# ============================================================
# EMERGENCY ALERTS
# ============================================================

class EmergencyAlertCreate(BaseModel):
    title: str
    message: str
    severity: str
    phone_numbers: List[str]
    created_by: str


# ============================================================
# SMS LOG
# ============================================================

class SMSLogResponse(BaseModel):
    id: int
    phone_number: str
    message: str
    message_type: MessageType
    provider: SMSProvider
    status: SMSStatus
    message_sid: Optional[str]
    error_message: Optional[str]
    cost: Optional[float]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
