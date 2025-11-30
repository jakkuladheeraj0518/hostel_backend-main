import firebase_admin
from firebase_admin import messaging
from app.models.push_models import NotificationPriority


async def send_fcm_notification(
    device_token: str,
    title: str,
    body: str,
    data: dict,
    priority: NotificationPriority
):
    """Send push notification via Firebase Cloud Messaging"""
    try:
        fcm_priority = "high" if priority in [NotificationPriority.high, NotificationPriority.urgent] else "normal"

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in data.items()},
            token=device_token,
        )

        message_id = messaging.send(message)
        return message_id, None

    except Exception as e:
        return None, str(e)
