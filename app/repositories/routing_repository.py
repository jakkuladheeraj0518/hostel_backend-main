# app/repository/routing_repository.py

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.routing_models import (
    
    RoutingRule,
    Notification,
    NotificationRecipient,
    EscalationLog,
    RoutingAuditLog,
    SupervisorAssignment,
    UserRole,
    NotificationPriority
)
from app.models.user import User
from app.schemas.routing_schemas import NotificationCreate


# ==========================================================
# USER REPOSITORY
# ==========================================================

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_users_by_role(db: Session, role, hostel_id=None):
    q = db.query(User).filter(
        User.role == role,
        User.is_active == True
    )

    if hostel_id:
        q = q.filter(User.hostel_id == hostel_id)

    return q.all()


# ==========================================================
# ROUTING RULE REPOSITORY
# ==========================================================

def get_applicable_routing_rule(db: Session, category, source_role, priority):
    """Original function used in some internal logic."""
    rules = db.query(RoutingRule).filter(
        RoutingRule.notification_category == category,
        RoutingRule.source_role == source_role,
        RoutingRule.is_active == True
    ).order_by(RoutingRule.priority_order.desc()).all()

    weights = {
        "low": 1, "normal": 2, "high": 3, "urgent": 4, "critical": 5
    }

    for rule in rules:
        if weights[priority.value] >= weights[rule.priority_threshold.value]:
            return rule

    return None


def get_routing_rule(db: Session, category, source_role, priority):
    """
    FINAL correct routing rule selector.
    This is the function the router calls:
    get_routing_rule(db, data.category, data.source_role, data.priority)
    """

    priority_weights = {
        NotificationPriority.low: 1,
        NotificationPriority.normal: 2,
        NotificationPriority.high: 3,
        NotificationPriority.urgent: 4,
        NotificationPriority.critical: 5
    }

    rules = (
        db.query(RoutingRule)
        .filter(
            RoutingRule.notification_category == category,
            RoutingRule.source_role == source_role,
            RoutingRule.is_active == True
        )
        .order_by(RoutingRule.priority_order.desc())
        .all()
    )

    for rule in rules:
        if priority_weights[priority] >= priority_weights[rule.priority_threshold]:
            return rule

    return None


def get_routing_rules(db: Session, category=None, source_role=None, active_only=True):
    q = db.query(RoutingRule)

    if active_only:
        q = q.filter(RoutingRule.is_active == True)
    if category:
        q = q.filter(RoutingRule.notification_category == category)
    if source_role:
        q = q.filter(RoutingRule.source_role == source_role)

    return q.order_by(RoutingRule.priority_order.desc()).all()


# ==========================================================
# NOTIFICATION CREATION
# ==========================================================

def create_notification_record(db: Session, data: NotificationCreate, rule):
    noti = Notification(
        source_user_id=data.source_user_id,
        source_role=data.source_role,
        hostel_id=data.hostel_id,
        category=data.category,
        priority=data.priority,
        title=data.title,
        message=data.message,
        extra_metadata=data.extra_metadata,
        reference_type=data.reference_type,
        reference_id=data.reference_id,
        routing_rule_id=rule.id if rule else None,
        routing_strategy=rule.routing_strategy if rule else "direct",
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(noti)
    db.commit()
    db.refresh(noti)

    return noti


# ==========================================================
# RECIPIENT MANAGEMENT
# ==========================================================

def add_recipients(db: Session, notification_id: int, primary_list, cc_list):
    """Legacy support: primary/cc separate lists."""

    for user in primary_list:
        rec = NotificationRecipient(
            notification_id=notification_id,
            user_id=user.id,
            user_role=user.role,
            recipient_type="primary",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(rec)

    for user in cc_list:
        rec = NotificationRecipient(
            notification_id=notification_id,
            user_id=user.id,
            user_role=user.role,
            recipient_type="cc",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(rec)

    db.commit()


def save_recipients(db: Session, notification_id: int, recipients: dict):
    """
    Router uses this version:
    recipients = { "primary": [...], "cc": [...] }
    """
    for user in recipients.get("primary", []):
        rec = NotificationRecipient(
            notification_id=notification_id,
            user_id=user.id,
            user_role=user.role,
            recipient_type="primary",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(rec)

    for user in recipients.get("cc", []):
        rec = NotificationRecipient(
            notification_id=notification_id,
            user_id=user.id,
            user_role=user.role,
            recipient_type="cc",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(rec)

    db.commit()


# ==========================================================
# ROUTING AUDIT LOG
# ==========================================================

def log_routing_decision(db: Session, notification_id, rule, recipients, time_ms):
    audit = RoutingAuditLog(
        notification_id=notification_id,
        rule_applied=rule.rule_name if rule else "default",
        routing_strategy=rule.routing_strategy if rule else "direct",
        source_user_id=None,
        target_user_ids=[u.id for u in recipients["primary"] + recipients["cc"]],
        decision_factors={},
        execution_time_ms=time_ms,
        created_at=datetime.utcnow()
    )
    db.add(audit)
    db.commit()


# ==========================================================
# SUPERVISOR / ADMIN LOOKUP
# ==========================================================

def get_supervisor_for_admin(db: Session, admin_id, hostel_id):
    assignment = db.query(SupervisorAssignment).filter(
        SupervisorAssignment.admin_id == admin_id,
        SupervisorAssignment.hostel_id == hostel_id,
        SupervisorAssignment.is_active == True
    ).first()

    if not assignment:
        return None

    return db.query(User).filter(User.id == assignment.supervisor_id).first()


def get_admin_for_supervisor(db: Session, supervisor_id):
    supervisor = db.query(User).filter(User.id == supervisor_id).first()

    if supervisor and supervisor.admin_id:
        return db.query(User).filter(User.id == supervisor.admin_id).first()

    return None


def get_admin_of_supervisor(db: Session, supervisor_id: int):
    """
    Required by router — this name MUST exist.
    """
    supervisor = db.query(User).filter(
        User.id == supervisor_id,
        User.role == UserRole.hostel_supervisor
    ).first()

    if not supervisor or not supervisor.admin_id:
        return None

    return db.query(User).filter(
        User.id == supervisor.admin_id,
        User.role == UserRole.hostel_admin
    ).first()
