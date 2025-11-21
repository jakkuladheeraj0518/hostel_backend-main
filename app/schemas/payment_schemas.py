from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Enums imported from your models
from app.models.payment_models import (
    PaymentGateway,
    PaymentStatus,
    PaymentMethod,
    TransactionType,
    RefundStatus,
    ReminderType,
    ReminderChannel,
    ReminderStatus
)

# =====================================================================
# 🟦 GENERAL PAYMENT CREATION (User/Hostel Payments)
# =====================================================================

class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "INR"
    user_id: int
    hostel_id: int
    description: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: str
    gateway_order_id: Optional[str]
    payment_id: Optional[str]
    gateway: PaymentGateway
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: Optional[PaymentMethod]
    user_id: int
    hostel_id: int
    description: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 BOOKING PAYMENT SCHEMAS (Visitor/Admin Booking Payments)
# =====================================================================

class BookingPaymentCreate(BaseModel):
    booking_id: int
    payment_type: str
    amount: float
    currency: str = "INR"
    payment_method: Optional[str] = None
    payment_gateway: Optional[str] = None
    description: Optional[str] = None


class BookingPaymentResponse(BaseModel):
    id: Optional[int]
    booking_id: int
    payment_reference: Optional[str]
    payment_type: str
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    payment_gateway: Optional[str]
    gateway_transaction_id: Optional[str]
    gateway_order_id: Optional[str]
    is_security_deposit: bool
    security_deposit_refunded: bool
    initiated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 RAZORPAY ORDER
# =====================================================================

class RazorpayOrderResponse(BaseModel):
    order_id: str
    gateway_order_id: str
    amount: float
    currency: str
    key_id: str
    payment_record_id: int


class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class CreateOrderRequest(BaseModel):
    amount: float
    currency: str = "INR"
    hostel_id: int
    description: Optional[str] = None


# =====================================================================
# 🟦 REFUND MODELS (Unified)
# =====================================================================


# Add RefundRequest for compatibility with payment_routers.py
class RefundRequest(BaseModel):
    payment_id: str | int
    amount: Optional[float] = None
    reason: Optional[str] = None

class RefundCreate(BaseModel):
    payment_id: str | int
    amount: Optional[float] = None
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: int
    payment_id: str | int
    refund_id: Optional[str]
    refund_reference: Optional[str] = None
    amount: float
    reason: Optional[str]
    status: str
    created_at: Optional[datetime]
    initiated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    invoice_id: Optional[int] = None
    transaction_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Security Deposit Release
# ---------------------------------------------------------------------

class SecurityDepositReleaseRequest(BaseModel):
    payment_id: int
    deduction_amount: float = 0.0
    reason: Optional[str] = None


class SecurityDepositReleaseResponse(BaseModel):
    message: str
    refund_amount: float
    deduction_amount: float
    payment_reference: str

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 INVOICE MODELS
# =====================================================================

class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    amount: float


class InvoiceCreate(BaseModel):
    user_id: int
    hostel_id: int
    items: List[InvoiceItem]
    description: Optional[str] = None
    due_date: datetime


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    user_id: int
    hostel_id: int
    total_amount: float
    paid_amount: float
    due_amount: float
    status: PaymentStatus
    issue_date: datetime
    due_date: datetime

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 TRANSACTION MODELS
# =====================================================================

class TransactionCreate(BaseModel):
    invoice_id: int
    amount: float = Field(gt=0)
    payment_method: str
    payment_gateway: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    invoice_id: int
    transaction_type: TransactionType
    amount: float
    payment_method: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 RECEIPT MODELS
# =====================================================================

class ReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    invoice_id: int
    transaction_id: int
    amount: float
    generated_at: datetime
    pdf_available: bool

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 REFUND APPROVAL WORKFLOW
# =====================================================================

class RefundApproval(BaseModel):
    approved_by: int
    approve: bool
    rejection_reason: Optional[str] = None


# =====================================================================
# 🟦 PAYMENT REMINDERS
# =====================================================================

class ReminderConfigCreate(BaseModel):
    hostel_id: int
    pre_due_days: str = "7,3,1"
    pre_due_channels: ReminderChannel = ReminderChannel.EMAIL
    due_date_enabled: bool = True
    due_date_channels: ReminderChannel = ReminderChannel.BOTH
    overdue_frequency_days: int = 3
    overdue_channels: ReminderChannel = ReminderChannel.BOTH
    escalation_enabled: bool = True
    escalation_1_days: int = 7
    escalation_2_days: int = 14
    escalation_3_days: int = 30
    final_notice_days: int = 45
    escalation_emails: Optional[List[str]] = None
    escalation_cc: Optional[List[str]] = None
    max_reminders: int = 10


class ReminderConfigResponse(BaseModel):
    id: int
    hostel_id: int
    pre_due_days: str
    overdue_frequency_days: int
    escalation_enabled: bool
    max_reminders: int

    class Config:
        from_attributes = True


class ManualReminderRequest(BaseModel):
    invoice_id: int
    reminder_type: ReminderType
    channel: ReminderChannel
    custom_message: Optional[str] = None


class PaymentReminderResponse(BaseModel):
    id: int
    reminder_id: str
    invoice_id: int
    reminder_type: ReminderType
    channel: ReminderChannel
    status: ReminderStatus
    scheduled_at: datetime

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 TEMPLATE MANAGEMENT
# =====================================================================

class TemplateCreate(BaseModel):
    name: str
    reminder_type: ReminderType
    email_subject: str
    email_body: str
    sms_body: str


class TemplateResponse(BaseModel):
    id: int
    name: str
    reminder_type: ReminderType
    is_default: bool

    class Config:
        from_attributes = True


# =====================================================================
# 🟦 BOOKING CONFIRMATION PDF
# =====================================================================

class ConfirmationResponse(BaseModel):
    id: int
    booking_id: int
    confirmation_number: str
    confirmation_type: str
    pdf_content: str
    email_sent: bool
    generated_at: datetime

    class Config:
        from_attributes = True
