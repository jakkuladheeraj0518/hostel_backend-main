import os
from typing import Optional, Dict, Any

try:
    import firebase_admin
    from firebase_admin import messaging, credentials
except Exception:
    firebase_admin = None

from app.services.providers.base_provider import ProviderInterface


class FCMProvider(ProviderInterface):
    def __init__(self, cred_json_path: Optional[str] = None):
        self.cred_json_path = cred_json_path or os.getenv("FCM_SERVICE_ACCOUNT_JSON")
        if firebase_admin and self.cred_json_path:
            try:
                cred = credentials.Certificate(self.cred_json_path)
                # initialize_app will raise if already initialized, so guard
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                self.available = True
            except Exception:
                self.available = False
        else:
            self.available = False

    def send(self, to: str, subject: str, body: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.available:
            return {"success": False, "provider": "fcm", "response": "not_configured"}

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=subject, body=body),
                token=to,
            )
            resp = messaging.send(message)
            return {"success": True, "provider": "fcm", "response": resp}
        except Exception as exc:
            return {"success": False, "provider": "fcm", "response": str(exc)}
