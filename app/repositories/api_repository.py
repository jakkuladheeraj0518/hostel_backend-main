from sqlalchemy.orm import Session
from app.models.api_models import (
    NotificationTemplate,
    UnifiedNotificationLog,
    NotificationBatch,
    UserChannelPreference
)

# ----------------------------
# Template Repository
# ----------------------------

def get_template_by_name(db: Session, name: str):
    return db.query(NotificationTemplate).filter(
        NotificationTemplate.name == name,
        NotificationTemplate.is_active == True
    ).first()

def get_template_by_id(db: Session, template_id: int):
    return db.query(NotificationTemplate).filter(
        NotificationTemplate.id == template_id
    ).first()


# ----------------------------
# Notification Log Repository
# ----------------------------

def save_log(db: Session, log: UnifiedNotificationLog):
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ----------------------------
# Batch Repository
# ----------------------------

def create_batch(db: Session, batch: NotificationBatch):
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


# ----------------------------
# Preferences Repository
# ----------------------------

def get_preferences(db: Session, user_id: int):
    return db.query(UserChannelPreference).filter(
        UserChannelPreference.user_id == user_id
    ).first()

def save_preferences(db: Session, pref: UserChannelPreference):
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref
