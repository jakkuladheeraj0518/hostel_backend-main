import requests

from app.config import settings


def send_push_fcm(device_token: str, title: str, body: str) -> dict:
    """
    Firebase Cloud Messaging for push notifications.

    Env needed:
      - FCM_SERVER_KEY
    """
    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": body,
        },
    }
    resp = requests.post(
        "https://fcm.googleapis.com/fcm/send", headers=headers, json=data
    )
    return {
        "status_code": resp.status_code,
        "body": resp.text,
        "headers": dict(resp.headers),
    }
