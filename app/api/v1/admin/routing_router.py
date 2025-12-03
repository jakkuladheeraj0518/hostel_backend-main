
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.config import get_db
from app.schemas.routing_schemas import (
    UserCreate, UserResponse,
    RoutingRuleCreate, RoutingRuleResponse,
    NotificationCreate, NotificationResponse,
    EscalateNotificationRequest,
    SupervisorAssignmentCreate
)
from app.models.routing_models import (
    RoutingRule, Notification, NotificationRecipient,
    EscalationLog, NotificationStatus, NotificationCategory,
    NotificationPriority, RoutingStrategy, EscalationLevel
)
from app.models.user import User
from app.services.routing_services import determine_recipients, escalate_notification
from app.repositories.routing_repository import (
    get_routing_rule,
    create_notification_record,
    save_recipients,
    get_admin_of_supervisor
)

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)

router = APIRouter(prefix="/api", tags=["Notification Routing Engine"])


# -----------------------------------------------------------
# USER MANAGEMENT
# -----------------------------------------------------------
@router.post("/create")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    data = user.dict()
    if not data.get("username"):
        data["username"] = data["email"].split("@")[0]

    obj = User(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    )
):
    obj = db.query(User).filter(User.id == user_id).first()
    if not obj:
        raise HTTPException(404, "User not found")
    return obj


# -----------------------------------------------------------
# SUPERVISOR ASSIGNMENT
# -----------------------------------------------------------
@router.post("/supervisor-assignments/")
def create_assignment(
    data: SupervisorAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    supervisor = db.query(User).filter(
        User.id == data.supervisor_id,
        User.role == "supervisor"
    ).first()

    admin = db.query(User).filter(
        User.id == data.admin_id,
        User.role == "admin"
    ).first()

    if not supervisor or not admin:
        raise HTTPException(404, "Invalid admin or supervisor")

    supervisor.admin_id = data.admin_id
    db.commit()
    return {"message": "Supervisor assigned successfully"}


@router.get("/supervisor-assignments/admin/{admin_id}")
def get_supervisors(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    return db.query(User).filter(User.admin_id == admin_id).all()


@router.get("/supervisor-assignments/supervisor/{supervisor_id}")
def get_supervisor_admin(
    supervisor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    return get_admin_of_supervisor(db, supervisor_id)


# -----------------------------------------------------------
# ROUTING RULES
# -----------------------------------------------------------
@router.post("/routing-rules/", response_model=RoutingRuleResponse)
def create_rule(
    rule: RoutingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    obj = RoutingRule(**rule.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/routing-rules/", response_model=list[RoutingRuleResponse])
def list_rules(
    category: NotificationCategory = None,
    source_role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    q = db.query(RoutingRule).filter(RoutingRule.is_active == True)

    if category:
        q = q.filter(RoutingRule.notification_category == category)
    if source_role:
        q = q.filter(RoutingRule.source_role == source_role)

    return q.order_by(RoutingRule.priority_order.desc()).all()


@router.put("/routing-rules/{rule_id}", response_model=RoutingRuleResponse)
def update_rule(
    rule_id: int,
    rule: RoutingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    obj = db.query(RoutingRule).filter(RoutingRule.id == rule_id).first()
    if not obj:
        raise HTTPException(404, "Rule not found")

    for k, v in rule.dict().items():
        setattr(obj, k, v)

    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


# -----------------------------------------------------------
# NOTIFICATIONS - routing engine
# -----------------------------------------------------------
@router.post("/notifications/", response_model=NotificationResponse)
def create_notification_endpoint(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    )
):
    rule = get_routing_rule(db, data.category, data.source_role, data.priority)
    notif = create_notification_record(db, data, rule)
    recipients = determine_recipients(db, notif, rule)
    save_recipients(db, notif.id, recipients)
    return notif


@router.get("/notifications/{notification_id}")
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    )
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Not found")

    recipients = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == notification_id
    ).all()

    escalations = db.query(EscalationLog).filter(
        EscalationLog.notification_id == notification_id
    ).all()

    return {
        "notification": notif,
        "recipients": recipients,
        "escalations": escalations
    }


@router.put("/notifications/{notification_id}/resolve")
def resolve(
    notification_id: int,
    user_id: int,
    resolution_notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    )
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Not found")

    notif.status = NotificationStatus.resolved
    notif.resolved_at = datetime.utcnow()

    esc = db.query(EscalationLog).filter(
        EscalationLog.notification_id == notification_id
    ).first()

    if esc:
        esc.resolved = True
        esc.resolved_at = datetime.utcnow()
        esc.resolution_notes = resolution_notes

    db.commit()
    return {"message": "Resolved"}


# -----------------------------------------------------------
# MANUAL ESCALATION
# -----------------------------------------------------------
@router.post("/notifications/escalate")
def manual_escalation(
    data: EscalateNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    )
):
    notif = db.query(Notification).filter(Notification.id == data.notification_id).first()
    if not notif:
        raise HTTPException(404, "Not found")

    rule = db.query(RoutingRule).filter(RoutingRule.id == notif.routing_rule_id).first()

    escalate_notification(
        db,
        notif,
        rule,
        auto=False,
        reason=data.reason
    )

    return {"message": "Escalation successful"}


# -----------------------------------------------------------
# STATS (Admin Only)
# -----------------------------------------------------------
@router.get("/stats/escalations")
def escalation_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    )
):
    start = datetime.utcnow() - timedelta(days=days)

    q = db.query(EscalationLog).filter(EscalationLog.created_at >= start)

    return {
        "total": q.count(),
        "auto": q.filter(EscalationLog.auto_escalated == True).count(),
        "manual": q.filter(EscalationLog.auto_escalated == False).count(),
        "by_level": {
            lvl.value: q.filter(EscalationLog.escalation_level == lvl).count()
            for lvl in EscalationLevel
        }
    }


@router.get("/stats/supervisor/{supervisor_id}")
def supervisor_stats(
    supervisor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    days: int = 30
):
    start = datetime.utcnow() - timedelta(days=days)

    recs = db.query(NotificationRecipient).filter(
        NotificationRecipient.user_id == supervisor_id,
        NotificationRecipient.created_at >= start
    )

    total = recs.count()
    acknowledged = recs.filter(NotificationRecipient.acknowledged_at != None).count()

    return {
        "total_received": total,
        "acknowledged": acknowledged,
        "rate": f"{(acknowledged / total) * 100:.2f}%" if total else "0%"
    }


@router.get("/stats/admin/{admin_id}")
def admin_stats(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    days: int = 30
):
    start = datetime.utcnow() - timedelta(days=days)

    supervisors = db.query(User).filter(User.admin_id == admin_id).all()
    sup_ids = [s.id for s in supervisors]

    handled = db.query(NotificationRecipient).filter(
        NotificationRecipient.user_id.in_(sup_ids),
        NotificationRecipient.created_at >= start
    ).count()

    escalations = db.query(EscalationLog).filter(
        EscalationLog.to_user_id == admin_id
    ).count()

    return {
        "supervisors": len(supervisors),
        "handled_by_supervisors": handled,
        "escalations_to_admin": escalations
    }
