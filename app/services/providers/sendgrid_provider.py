import os
from typing import Optional, Dict, Any

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.services.providers.base_provider import ProviderInterface


class SendGridProvider(ProviderInterface):
    def __init__(self, api_key: Optional[str] = None, default_from: Optional[str] = None):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.default_from = default_from or os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None

    def send(self, to: str, subject: str, body: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.client:
            return {"success": False, "provider": "sendgrid", "response": "missing_api_key"}

        message = Mail(from_email=self.default_from, to_emails=to, subject=subject, html_content=body)
        try:
            resp = self.client.send(message)
            status = getattr(resp, "status_code", None)
            body = getattr(resp, "body", None)
            success = status is not None and 200 <= int(status) < 300
            return {"success": success, "provider": "sendgrid", "response": f"{status}:{body}"}
        except Exception as exc:
            return {"success": False, "provider": "sendgrid", "response": str(exc)}
