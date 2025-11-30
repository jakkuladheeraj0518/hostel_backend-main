from datetime import datetime, timedelta

from app.models.routing_models import (
    Notification, NotificationRecipient,
    NotificationStatus, RoutingRule, EscalationLog,
    EscalationLevel, UserRole
)
from app.models.user import User


# ------------------ ROUTING SERVICE ------------------

def determine_recipients(db, notification, rule):
    primary = []
    cc = []

    source = db.query(User).filter(User.id == notification.source_user_id).first()

    if not rule:
        admins = db.query(User).filter(
            User.role == UserRole.hostel_admin,
            User.hostel_id == notification.hostel_id,
            User.is_active == True
        ).all()
        return {"primary": admins, "cc": []}

    if rule.routing_strategy == "hierarchical":

        if source.role == UserRole.student:
            supervisors = db.query(User).filter(
                User.role == UserRole.hostel_supervisor,
                User.hostel_id == notification.hostel_id
            ).all()
            primary.extend(supervisors)

    # more logic (same as main.py logic)

    return {"primary": primary, "cc": cc}


# ------------------ ESCALATION SERVICE ------------------

def escalate_notification(db, notification, rule, auto=False, reason="Auto Escalation"):

    recipients = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == notification.id
    ).all()

    if not recipients:
        return

    current_role = recipients[0].user_role

    next_role = None

    if current_role == UserRole.hostel_supervisor:
        next_role = UserRole.hostel_admin
        level = EscalationLevel.LEVEL_1

    elif current_role == UserRole.hostel_admin:
        next_role = UserRole.super_admin
        level = EscalationLevel.LEVEL_2

    else:
        return

    target = db.query(User).filter(User.role == next_role).first()

    esc = EscalationLog(
        notification_id=notification.id,
        from_user_id=recipients[0].user_id,
        from_role=current_role,
        to_user_id=target.id,
        to_role=target.role,
        reason=reason,
        auto_escalated=auto,
        escalation_level=level,
        escalation_time_elapsed=5
    )

    db.add(esc)

    new = NotificationRecipient(
        notification_id=notification.id,
        user_id=target.id,
        user_role=target.role,
        recipient_type="escalated"
    )
    db.add(new)

    notification.status = NotificationStatus.escalated
    db.commit()
