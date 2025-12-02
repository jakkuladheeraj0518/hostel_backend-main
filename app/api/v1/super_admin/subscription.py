# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app import  schemas, services

# router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# # ───────────────────────────────────────────────────────────────
# # PLANS
# # ───────────────────────────────────────────────────────────────
# @router.post("/plans", response_model=schemas.SubscriptionPlanResponse)
# def create_plan(plan: schemas.SubscriptionPlanCreate, db: Session = Depends(get_db)):
#     return services.subscription_service.create_plan_service(db, plan)


# @router.get("/plans", response_model=list[schemas.SubscriptionPlanResponse])
# def list_plans(db: Session = Depends(get_db)):
#     return services.subscription_service.list_plans_service(db)


# # ───────────────────────────────────────────────────────────────
# # SUBSCRIPTIONS
# # ───────────────────────────────────────────────────────────────
# @router.post("/", response_model=schemas.SubscriptionResponse)
# def create_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
#     try:
#         return services.subscription_service.create_subscription_service(db, subscription)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/", response_model=list[schemas.SubscriptionResponse])
# def list_subscriptions(db: Session = Depends(get_db)):
#     return services.subscription_service.list_subscriptions_service(db)


# # ───────────────────────────────────────────────────────────────
# # PAYMENTS
# # ───────────────────────────────────────────────────────────────
# @router.post("/Organisationpayments", response_model=schemas.organizationPaymentResponse)
# def create_payment(payment: schemas.organizationPaymentCreate, db: Session = Depends(get_db)):
#     return services.subscription_service.create_payment_service(db, payment)


# @router.get("/Organisationpayments", response_model=list[schemas.organizationPaymentResponse])
# def list_payments(subscription_id: str = None, db: Session = Depends(get_db)):
#     return services.subscription_service.list_payments_service(db, subscription_id)


# # ───────────────────────────────────────────────────────────────
# # CHANGES
# # ───────────────────────────────────────────────────────────────
# @router.post("/changes", response_model=schemas.SubscriptionChangeResponse)
# def create_change(change: schemas.SubscriptionChangeCreate, db: Session = Depends(get_db)):
#     return services.subscription_service.create_change_service(db, change)


# @router.get("/changes/{subscription_id}", response_model=list[schemas.SubscriptionChangeResponse])
# def list_changes(subscription_id: str, db: Session = Depends(get_db)):
#     return services.subscription_service.list_changes_service(db, subscription_id)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import schemas, services

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ───────────────────────────────────────────────────────────────
# PLANS
# ───────────────────────────────────────────────────────────────
@router.post("/plans", response_model=schemas.SubscriptionPlanResponse)
def create_plan(
    plan: schemas.SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_SUBSCRIPTIONS)),
):
    return services.subscription_service.create_plan_service(db, plan)


@router.get("/plans", response_model=list[schemas.SubscriptionPlanResponse])
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_SUBSCRIPTIONS)),
):
    return services.subscription_service.list_plans_service(db)


# ───────────────────────────────────────────────────────────────
# SUBSCRIPTIONS
# ───────────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.SubscriptionResponse)
def create_subscription(
    subscription: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_SUBSCRIPTIONS)),
):
    try:
        return services.subscription_service.create_subscription_service(db, subscription)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[schemas.SubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_SUBSCRIPTIONS)),
):
    return services.subscription_service.list_subscriptions_service(db)


# ───────────────────────────────────────────────────────────────
# PAYMENTS
# ───────────────────────────────────────────────────────────────
@router.post("/Organisationpayments", response_model=schemas.organizationPaymentResponse)
def create_payment(
    payment: schemas.organizationPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_PAYMENTS)),
):
    return services.subscription_service.create_payment_service(db, payment)


@router.get("/Organisationpayments", response_model=list[schemas.organizationPaymentResponse])
def list_payments(
    subscription_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.VIEW_PAYMENTS)),
):
    return services.subscription_service.list_payments_service(db, subscription_id)


# ───────────────────────────────────────────────────────────────
# CHANGES
# ───────────────────────────────────────────────────────────────
@router.post("/changes", response_model=schemas.SubscriptionChangeResponse)
def create_change(
    change: schemas.SubscriptionChangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_SUBSCRIPTIONS)),
):
    return services.subscription_service.create_change_service(db, change)


@router.get("/changes/{subscription_id}", response_model=list[schemas.SubscriptionChangeResponse])
def list_changes(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_SUBSCRIPTIONS)),
):
    return services.subscription_service.list_changes_service(db, subscription_id)
