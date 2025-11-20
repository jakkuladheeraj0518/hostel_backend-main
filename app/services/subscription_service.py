from sqlalchemy.orm import Session
from app import schemas, repositories
from datetime import datetime


def create_plan_service(db: Session, plan: schemas.SubscriptionPlanCreate):
    return repositories.subscription_repository.create_plan(db, plan)


def list_plans_service(db: Session):
    return repositories.subscription_repository.get_all_plans(db)


def create_subscription_service(db: Session, subscription: schemas.SubscriptionCreate):
    existing = repositories.subscription_repository.get_subscription_by_org(db, subscription.organization_id)
    if existing:
        raise ValueError("Organization already has an active subscription")
    return repositories.subscription_repository.create_subscription(db, subscription)


def list_subscriptions_service(db: Session):
    return repositories.subscription_repository.list_subscriptions(db)


def create_payment_service(db: Session, payment: schemas.PaymentCreate):
    # stamp when payment was created/recorded
    payment.paid_at = datetime.utcnow()

    # Ensure the subscription exists. callers may pass either a subscription.id
    # or an organization_id (legacy/tests). Try subscription id first, then
    # fall back to organization lookup and map to the real subscription id.
    sub = repositories.subscription_repository.get_subscription_by_id(db, payment.subscription_id)
    if not sub:
        sub = repositories.subscription_repository.get_subscription_by_org(db, payment.subscription_id)
        if sub:
            # mutate schema value so repository will use the correct fk
            payment.subscription_id = sub.id
        else:
            raise ValueError(f"Subscription not found for id or organization_id: {payment.subscription_id}")

    return repositories.subscription_repository.create_payment(db, payment)


def list_payments_service(db: Session, subscription_id: str = None):
    return repositories.subscription_repository.list_payments(db, subscription_id)


def create_change_service(db: Session, change: schemas.SubscriptionChangeCreate):
    return repositories.subscription_repository.create_change(db, change)


def list_changes_service(db: Session, subscription_id: str):
    return repositories.subscription_repository.list_changes(db, subscription_id)
