from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ───────────────────────────────────────────────────────────────
# ENUMS
# ───────────────────────────────────────────────────────────────
class PlanTier(str, Enum):
    free = "free"
    standard = "standard"
    premium = "premium"


class BillingCycle(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class SubscriptionStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    canceled = "canceled"
    past_due = "past_due"
    trialing = "trialing"


class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"


class PaymentType(str, Enum):
    subscription = "subscription"
    upgrade = "upgrade"
    downgrade = "downgrade"
    refund = "refund"
    proration = "proration"


class ChangeType(str, Enum):
    upgrade = "upgrade"
    downgrade = "downgrade"
    cancel = "cancel"
    reactivate = "reactivate"


# ───────────────────────────────────────────────────────────────
# PLAN SCHEMAS
# ───────────────────────────────────────────────────────────────
class SubscriptionPlanBase(BaseModel):
    name: str
    tier: PlanTier
    billing_cycle: BillingCycle
    price: float
    currency: str = "USD"
    max_hostels: int
    max_admins: int
    max_students: int
    features: Optional[Any] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ───────────────────────────────────────────────────────────────
# SUBSCRIPTION SCHEMAS
# ───────────────────────────────────────────────────────────────
class SubscriptionBase(BaseModel):
    organization_id: str
    organization_name: str
    email: EmailStr
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.active
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: str
    cancel_at_period_end: bool
    canceled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ───────────────────────────────────────────────────────────────
# PAYMENT SCHEMAS
# ───────────────────────────────────────────────────────────────
class organizationPaymentBase(BaseModel):
    subscription_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.pending
    payment_type: PaymentType = PaymentType.subscription
    payment_method: Optional[str] = None
    payment_method_last4: Optional[str] = None
    description: Optional[str] = None




class organizationPaymentCreate(organizationPaymentBase):
    paid_at: Optional[datetime] = None


class organizationPaymentResponse(organizationPaymentBase):
    id: str
    paid_at: Optional[datetime]
    failed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }


# ───────────────────────────────────────────────────────────────
# SUBSCRIPTION CHANGE SCHEMAS
# ───────────────────────────────────────────────────────────────
class SubscriptionChangeBase(BaseModel):
    subscription_id: str
    change_type: ChangeType
    from_plan_id: Optional[str] = None
    to_plan_id: Optional[str] = None
    proration_amount: float = 0
    effective_date: datetime
    initiated_by: str
    reason: Optional[str] = None


class SubscriptionChangeCreate(SubscriptionChangeBase):
    pass


class SubscriptionChangeResponse(SubscriptionChangeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
