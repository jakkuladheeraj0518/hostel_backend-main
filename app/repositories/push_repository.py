from sqlalchemy.orm import Session
from app.models.push_models import NotificationPreference


def get_user_preferences(db: Session, user_id: int):
    return db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()


def check_user_allows(db: Session, user_id: int, ntype):
    pref = get_user_preferences(db, user_id)
    if not pref:
        return True

    if ntype == "emergency_alert":
        return True

    mapping = {
        "announcement": pref.announcement_enabled,
        "payment_reminder": pref.payment_reminder_enabled,
        "complaint_update": pref.complaint_update_enabled,
        "maintenance_update": pref.maintenance_update_enabled,
        "attendance_alert": pref.attendance_alert_enabled,
        "booking_update": pref.booking_update_enabled,
        "mess_menu": pref.mess_menu_enabled,
        "leave_approval": pref.leave_approval_enabled,
    }

    return mapping.get(ntype, True)
