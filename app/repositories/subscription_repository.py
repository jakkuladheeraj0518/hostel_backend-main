from sqlalchemy.orm import Session
from app.models import subscription as subscription_models
from app import schemas
from typing import List, Optional


# ───────────────────────────────────────────────────────────────
# PLAN REPOSITORY
# ───────────────────────────────────────────────────────────────
def create_plan(db: Session, plan: schemas.SubscriptionPlanCreate):
    db_plan = subscription_models.SubscriptionPlan(**plan.dict(by_alias=True))
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_all_plans(db: Session) -> List[subscription_models.SubscriptionPlan]:
    return db.query(subscription_models.SubscriptionPlan).filter(subscription_models.SubscriptionPlan.is_active == True).all()


def get_plan_by_id(db: Session, plan_id: str):
    return db.query(subscription_models.SubscriptionPlan).filter(subscription_models.SubscriptionPlan.id == plan_id).first()


# ───────────────────────────────────────────────────────────────
# SUBSCRIPTION REPOSITORY
# ───────────────────────────────────────────────────────────────
def create_subscription(db: Session, subscription: schemas.SubscriptionCreate):
    db_sub = subscription_models.Subscription(**subscription.dict(by_alias=True))
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def get_subscription_by_org(db: Session, organization_id: str):
    return db.query(subscription_models.Subscription).filter(subscription_models.Subscription.organization_id == organization_id).first()


def get_subscription_by_id(db: Session, subscription_id: str):
    return db.query(subscription_models.Subscription).filter(subscription_models.Subscription.id == subscription_id).first()


def list_subscriptions(db: Session) -> List[subscription_models.Subscription]:
    return db.query(subscription_models.Subscription).all()


# ───────────────────────────────────────────────────────────────
# PAYMENT REPOSITORY
# ───────────────────────────────────────────────────────────────
def create_payment(db: Session, payment: schemas.PaymentCreate):
    payment_data = payment.dict(by_alias=True, exclude_unset=True)
    # Handle metadata separately since it's an aliased field
    if hasattr(payment, 'metadata_') and payment.metadata_ is not None:
        payment_data['metadata_'] = payment.metadata_
    
    db_payment = subscription_models.Payment(**payment_data)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Convert metadata to dict for response if present
    if db_payment.metadata_ is not None:
        db_payment.metadata_ = dict(db_payment.metadata_)
    return db_payment


def list_payments(db: Session, subscription_id: Optional[str] = None):
    query = db.query(subscription_models.Payment)
    if subscription_id:
        query = query.filter(subscription_models.Payment.subscription_id == subscription_id)
    payments = query.all()
    # Convert SQLAlchemy metadata to dict or None
    for payment in payments:
        if hasattr(payment, 'metadata_') and payment.metadata_ is not None:
            payment.metadata_ = dict(payment.metadata_)
    return payments


# ───────────────────────────────────────────────────────────────
# SUBSCRIPTION CHANGES REPOSITORY
# ───────────────────────────────────────────────────────────────
def create_change(db: Session, change: schemas.SubscriptionChangeCreate):
    db_change = subscription_models.SubscriptionChange(**change.dict(by_alias=True))
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    return db_change


def list_changes(db: Session, subscription_id: str):
    return db.query(subscription_models.SubscriptionChange).filter(subscription_models.SubscriptionChange.subscription_id == subscription_id).all()
