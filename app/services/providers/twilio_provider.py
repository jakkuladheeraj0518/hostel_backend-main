import os
from typing import Optional, Dict, Any

from twilio.rest import Client

from app.services.providers.base_provider import ProviderInterface


class TwilioProvider(ProviderInterface):
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, from_number: Optional[str] = None):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid and self.auth_token else None

    def send(self, to: str, subject: str, body: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Twilio SMS doesn't use subject — we include it in the body if present
        if not self.client:
            return {"success": False, "provider": "twilio", "response": "missing_credentials"}

        message_body = (subject + "\n" + body) if subject else body
        try:
            msg = self.client.messages.create(body=message_body, from_=self.from_number, to=to)
            return {"success": True, "provider": "twilio", "response": getattr(msg, "sid", str(msg))}
        except Exception as exc:
            return {"success": False, "provider": "twilio", "response": str(exc)}
