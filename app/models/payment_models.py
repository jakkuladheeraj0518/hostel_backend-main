from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Text, Boolean
from datetime import datetime
from enum import Enum
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Text, Boolean, ForeignKey



class PaymentStatus(str, Enum):
    PENDING = "pending"
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentGateway(str, Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    PAYTM = "paytm"

class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)



from sqlalchemy import ForeignKey

# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(String, unique=True, nullable=False, index=True)
#     gateway_order_id = Column(String, unique=True, index=True)
#     payment_id = Column(String, unique=True, index=True)
#     gateway = Column(SQLEnum(PaymentGateway), nullable=False)
#     amount = Column(Float, nullable=False)
#     currency = Column(String, default="INR")
#     status = Column(
#     SQLEnum(PaymentStatus, name="paymentstatus", native_enum=False),
#     default=PaymentStatus.PENDING.value
# )

#     payment_method = Column(SQLEnum(PaymentMethod), nullable=True)

#     user_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)

#     description = Column(String)
#     notes = Column(Text)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     paid_at = Column(DateTime, nullable=True)

#     # ✅ Relationships
#     customer = relationship("Customer")
#     hostel = relationship("Hostel", back_populates="payments")
#     transactions = relationship("Transaction", back_populates="payment", cascade="all, delete-orphan")
#     receipts = relationship("Receipt", back_populates="payment", cascade="all, delete-orphan")



class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"
    id = Column(Integer, primary_key=True, index=True)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    payment_id = Column(String, index=True)
    order_id = Column(String, index=True)
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, nullable=False, index=True)
    refund_id = Column(String, unique=True, nullable=False)
    gateway_refund_id = Column(String, unique=True)
    amount = Column(Float, nullable=False)
    reason = Column(String)
    status = Column(String, default="pending")
    gateway_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
#payments, partial payments, refunds, customers, and generates PDF receipts.
# app/models/payment_models.py
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class RefundStatus(str, Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    hostel_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("customers.id"), nullable=False)  
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    due_amount = Column(Float, nullable=False)
    description = Column(Text)
    items = Column(Text)  # store JSON string
    status = Column(
    SQLEnum(PaymentStatus, name="paymentstatus", native_enum=False),
    default=PaymentStatus.PENDING.value
)

    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ Relationships
    transactions = relationship(
        "Transaction", back_populates="invoice", cascade="all, delete-orphan"
    )
    receipts = relationship(
        "Receipt", back_populates="invoice", cascade="all, delete-orphan"
    )
    hostel = relationship("Hostel", back_populates="invoices")
    reminders = relationship("PaymentReminder", back_populates="invoice", cascade="all, delete-orphan")



# -------------------------------------------------------------------
# 💳 TRANSACTION MODEL
# -------------------------------------------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    payment_id = Column(String, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)

    #payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)

    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)

    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String)
    payment_gateway = Column(String)
    gateway_transaction_id = Column(String)
    status = Column(String, default="success")
    notes = Column(Text)
    processed_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships
    payment = relationship("Payment", back_populates="transactions")  # this line fixes the error

    invoice = relationship("Invoice", back_populates="transactions")
    receipt = relationship("Receipt", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    refund_requests = relationship("RefundRequest", back_populates="transaction", cascade="all, delete-orphan")


# -------------------------------------------------------------------
# 🧾 RECEIPT MODEL
# -------------------------------------------------------------------
class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    #payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(String, ForeignKey("payments.id", ondelete="CASCADE"))

    amount = Column(Float, nullable=False)
    pdf_path = Column(String)
    qr_code_data = Column(String)
    is_emailed = Column(Boolean, default=False)
    email_sent_at = Column(DateTime)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships
    invoice = relationship("Invoice", back_populates="receipts")
    transaction = relationship("Transaction", back_populates="receipt")
    payment = relationship("Payment", back_populates="receipts")



# -------------------------------------------------------------------
# 💸 REFUND REQUEST MODEL
# -------------------------------------------------------------------
class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)
    refund_id = Column(String, unique=True, nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    refund_amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(
    SQLEnum(RefundStatus, name="refundstatus", native_enum=False),
    default=RefundStatus.INITIATED.value
)

    requested_by = Column(Integer, nullable=False)
    approved_by = Column(Integer)
    rejection_reason = Column(Text)
    gateway_refund_id = Column(String)
    gateway_response = Column(Text)
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)

    # ✅ Relationships
    transaction = relationship("Transaction", back_populates="refund_requests")
    invoice = relationship("Invoice")

# -------------------------------------------------------------------
# 🔔 PAYMENT REMINDER MODELS

class ReminderType(str, Enum):
    PRE_DUE = "pre_due"
    DUE_DATE = "due_date"
    OVERDUE = "overdue"
    ESCALATION_1 = "escalation_1"
    ESCALATION_2 = "escalation_2"
    ESCALATION_3 = "escalation_3"
    FINAL_NOTICE = "final_notice"

class ReminderChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"

class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"



# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     phone = Column(String)
#     hostel_id = Column(Integer, ForeignKey("hostels.id"))
#     email_notifications = Column(Boolean, default=True)
#     sms_notifications = Column(Boolean, default=True)

#     created_at = Column(DateTime, default=datetime.utcnow)

#     invoices = relationship("Invoice", back_populates="user")




class ReminderConfiguration(Base):
    __tablename__ = "reminder_configurations"

    id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), unique=True)

    pre_due_days = Column(String, default="7,3,1")
    pre_due_channels = Column(SQLEnum(ReminderChannel), default=ReminderChannel.EMAIL)

    due_date_enabled = Column(Boolean, default=True)
    due_date_channels = Column(SQLEnum(ReminderChannel), default=ReminderChannel.BOTH)

    overdue_frequency_days = Column(Integer, default=3)
    overdue_channels = Column(SQLEnum(ReminderChannel), default=ReminderChannel.BOTH)

    escalation_enabled = Column(Boolean, default=True)
    escalation_1_days = Column(Integer, default=7)
    escalation_2_days = Column(Integer, default=14)
    escalation_3_days = Column(Integer, default=30)
    final_notice_days = Column(Integer, default=45)

    escalation_emails = Column(String)
    escalation_cc = Column(String)
    max_reminders = Column(Integer, default=10)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hostel = relationship("Hostel", back_populates="reminder_config")



class PaymentReminder(Base):
    __tablename__ = "payment_reminders"

    id = Column(Integer, primary_key=True)
    reminder_id = Column(String, unique=True, nullable=False)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    reminder_type = Column(SQLEnum(ReminderType), nullable=False)
    channel = Column(SQLEnum(ReminderChannel), nullable=False)

    recipient_email = Column(String)
    recipient_phone = Column(String)

    subject = Column(String)
    message_body = Column(Text)

    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.PENDING)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)

    error_message = Column(Text)
    delivery_status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="reminders")


class ReminderTemplate(Base):
    __tablename__ = "reminder_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    reminder_type = Column(SQLEnum(ReminderType))

    email_subject = Column(String)
    email_body = Column(Text)
    sms_body = Column(String)

    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
