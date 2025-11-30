from jinja2 import Template
from sqlalchemy.orm import Session
from typing import Dict, List


from app.models.api_models import UserChannelPreference, NotificationCategory


# ============================================================
# TEMPLATE RENDERER
# ============================================================

def render_template(template: str, variables: Dict) -> str:
    """Render notification template using Jinja2."""
    if not template:
        return ""
    return Template(template).render(**variables)


# ============================================================
# USER CHANNEL PREFERENCE RESOLUTION
# ============================================================

def get_user_channel_preferences(db: Session, user_id: int, category: NotificationCategory) -> List[str]:
    pref = db.query(UserChannelPreference).filter(
        UserChannelPreference.user_id == user_id
    ).first()

    if not pref:
        if category == NotificationCategory.emergency:
            return ["email", "sms", "push"]
        return ["email", "push"]

    category_map = {
        NotificationCategory.complaint: pref.complaint_channels,
        NotificationCategory.maintenance: pref.maintenance_channels,
        NotificationCategory.attendance: pref.attendance_channels,
        NotificationCategory.payment: pref.payment_channels,
        NotificationCategory.booking: pref.booking_channels,
        NotificationCategory.announcement: pref.announcement_channels,
        NotificationCategory.emergency: pref.emergency_channels,
    }

    channels = category_map.get(category, ["email", "push"])

    if not pref.email_enabled and "email" in channels:
        channels.remove("email")
    if not pref.sms_enabled and "sms" in channels:
        channels.remove("sms")
    if not pref.push_enabled and "push" in channels:
        channels.remove("push")

    return channels
