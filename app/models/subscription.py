from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Numeric, Integer, JSON, Enum as SQLEnum,
    Boolean, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum
from datetime import datetime
from enum import Enum



class PlanTier(str, enum.Enum):
    free = "free"
    standard = "standard"
    premium = "premium"


class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"

class PaymentGateway(str, Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    PAYTM = "paytm"

class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"

class SubscriptionStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    canceled = "canceled"
    past_due = "past_due"
    trialing = "trialing"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"
    initiated = "initiated"
    # SUCCESS = "success"



class PaymentType(str, enum.Enum):
    subscription = "subscription"
    upgrade = "upgrade"
    downgrade = "downgrade"
    refund = "refund"
    proration = "proration"


class ChangeType(str, enum.Enum):
    upgrade = "upgrade"
    downgrade = "downgrade"
    cancel = "cancel"
    reactivate = "reactivate"


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String, primary_key=True, default=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    tier = Column(SQLEnum(PlanTier, name="plan_tier"), nullable=False, index=True)
    billing_cycle = Column(SQLEnum(BillingCycle, name="billing_cycle"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD")

    # Plan Features
    max_hostels = Column(Integer, nullable=False)
    max_admins = Column(Integer, nullable=False)
    max_students = Column(Integer, nullable=False)
    features = Column(JSON)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    organization_id = Column(String, nullable=False, index=True)
    organization_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    plan_id = Column(String, ForeignKey('subscription_plans.id'), nullable=False)

    status = Column(SQLEnum(SubscriptionStatus, name="subscription_status"), default=SubscriptionStatus.active)

    # Billing
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_end = Column(DateTime, nullable=True)

    # Usage tracking
    current_hostels = Column(Integer, default=0)
    current_admins = Column(Integer, default=0)
    current_students = Column(Integer, default=0)

    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    # Relationship to organization-level payments (subscription billing)
    organization_payments = relationship(
        "organizationPayment",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )
    # Relationship to generic payments (Payment model)
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    changes = relationship("SubscriptionChange", back_populates="subscription", cascade="all, delete-orphan")


class organizationPayment(Base):
    __tablename__ = "organization_payments"

    id = Column(String, primary_key=True, default=lambda: f"pay_{uuid.uuid4().hex[:8]}")
    subscription_id = Column(String, ForeignKey('subscriptions.id', ondelete='CASCADE'), nullable=False)

    hostel_id = Column(Integer, ForeignKey("hostels.id"))        # ADDED
    # This relationship should not use the generic 'payments' back_populates
    # because `Hostel.payments` refers to the `Payment` model. Use a
    # distinct attribute name on `Hostel` so the back_populates pair matches.
    hostel = relationship("Hostel", back_populates="organization_payments")

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD")
    status = Column(SQLEnum(PaymentStatus, name="payment_status"), default=PaymentStatus.pending)
    payment_type = Column(SQLEnum(PaymentType, name="payment_type"), default=PaymentType.subscription)

    payment_method = Column(String)
    payment_method_last4 = Column(String)

    description = Column(Text)
    metadata_ = Column('metadata', JSON)

    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Link back to Subscription.organization_payments
    subscription = relationship("Subscription", back_populates="organization_payments")

class Payment(Base):
    __tablename__ = "payments"

    # -----------------------------------
    # IDs
    # -----------------------------------
    id = Column(String, primary_key=True, default=lambda: f"pay_{uuid.uuid4().hex[:8]}")
    order_id = Column(String, unique=True, nullable=True, index=True)            # MERGED
    gateway_order_id = Column(String, unique=True, index=True)                   # MERGED
    payment_id = Column(String, unique=True, index=True)                         # MERGED

    # -----------------------------------
    # Foreign Keys
    # -----------------------------------
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)         # MERGED
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)        # FROM BOTH MODELS

    # -----------------------------------
    # Payment Details
    # -----------------------------------
    amount = Column(Numeric(10, 2), nullable=False)                              # BASE MODEL
    currency = Column(String, default="USD")                                     # BASE MODEL

    gateway = Column(SQLEnum(PaymentGateway), nullable=True)                     # MERGED

    status = Column(
        SQLEnum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.pending
    )                                                                             # BASE MODEL

    payment_type = Column(
        SQLEnum(PaymentType, name="payment_type"),
        default=PaymentType.subscription
    )                                                                             # BASE MODEL

    payment_method = Column(String)                                              # BASE MODEL
    payment_method_last4 = Column(String)                                        # BASE MODEL
    payment_method_enum = Column(SQLEnum(PaymentMethod), nullable=True)          # MERGED (renamed)

    # -----------------------------------
    # Metadata & Notes
    # -----------------------------------
    description = Column(Text)
    notes = Column(Text)                                                         # MERGED
    metadata_ = Column("metadata", JSON)

    # -----------------------------------
    # Timestamps
    # -----------------------------------
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # -----------------------------------
    # Relationships
    # -----------------------------------
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User", back_populates="payments")        # BASE MODEL
    # customer = relationship("Customer")                                           # MERGED
    hostel = relationship("Hostel", back_populates="payments")                    # BOTH MODELS

    transactions = relationship(
        "Transaction",
        back_populates="payment",
        cascade="all, delete-orphan"
    )                                                                             # MERGED

    receipts = relationship(
        "Receipt",
        back_populates="payment",
        cascade="all, delete-orphan"
    )                                                                             # MERGED


class SubscriptionChange(Base):
    __tablename__ = "subscription_changes"

    id = Column(String, primary_key=True, default=lambda: f"change_{uuid.uuid4().hex[:8]}")
    subscription_id = Column(String, ForeignKey('subscriptions.id', ondelete='CASCADE'), nullable=False)

    change_type = Column(SQLEnum(ChangeType, name="change_type"), nullable=False)
    from_plan_id = Column(String, ForeignKey('subscription_plans.id'), nullable=True)
    to_plan_id = Column(String, ForeignKey('subscription_plans.id'), nullable=True)

    proration_amount = Column(Numeric(10, 2), default=0)

    effective_date = Column(DateTime, nullable=False)
    initiated_by = Column(String, nullable=False)
    reason = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    subscription = relationship("Subscription", back_populates="changes")
    from_plan = relationship("SubscriptionPlan", foreign_keys=[from_plan_id])
    to_plan = relationship("SubscriptionPlan", foreign_keys=[to_plan_id])
  