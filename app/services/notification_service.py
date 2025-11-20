from typing import Dict, Any, Optional
import os

from jinja2 import Template
from datetime import datetime

from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification, NotificationTemplate, Channel, DeliveryAttempt

# FIXED: No circular import – interface separated
from app.services.providers.base_provider import ProviderInterface

# Providers (these must import interface from the base_provider)
from app.services.providers.sendgrid_provider import SendGridProvider
from app.services.providers.twilio_provider import TwilioProvider
from app.services.providers.fcm_provider import FCMProvider

# remove this top-level import if present:
# from app.tasks.notification_tasks import enqueue_send


class DummyEmailProvider(ProviderInterface):
    """Used when real email provider is missing."""
    def send(self, to: str, subject: str, body: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"success": True, "provider": "dummy_email", "response": "ok"}


class NotificationService:
    def __init__(self, db):
        self.repo = NotificationRepository(db)

        # Providers (optional)
        self.sendgrid = SendGridProvider(os.getenv("SENDGRID_API_KEY")) if os.getenv("SENDGRID_API_KEY") else None
        self.twilio = TwilioProvider(os.getenv("TWILIO_ACCOUNT_SID")) if os.getenv("TWILIO_ACCOUNT_SID") else None
        self.fcm = FCMProvider(os.getenv("FCM_SERVICE_ACCOUNT_JSON")) if os.getenv("FCM_SERVICE_ACCOUNT_JSON") else None

    def provider_status(self) -> dict:
        """Return availability/status for providers."""
        return {
            "sendgrid": bool(self.sendgrid and getattr(self.sendgrid, "client", None)),
            "twilio": bool(self.twilio and getattr(self.twilio, "client", None)),
            "fcm": bool(self.fcm and getattr(self.fcm, "available", False)),
        }

    def route_recipients(self, recipient_id: str, recipient_type: str) -> list:
        """Return an ordered list of (recipient_id, recipient_type) to attempt delivery.

        This is a simple in-memory hierarchical routing example:
        - first: the original recipient
        - second: supervisor for the student (if student)
        - third: default admin
        In a real system this would consult user relations in the DB.
        """
        routed = [(recipient_id, recipient_type)]
        if recipient_type == "student":
            # synthetic supervisor id for demo purposes
            routed.append((f"supervisor_for_{recipient_id}", "supervisor"))
        # finally add a default admin contact
        routed.append(("admin_default", "admin"))
        return routed

    # ------------------------------ #
    #   TEMPLATE RENDERING
    # ------------------------------ #
    def render_template(self, template: NotificationTemplate, context: Dict[str, Any]) -> Dict[str, str]:
        subject = Template(template.subject_template or "").render(**(context or {}))
        body = Template(template.body_template or "").render(**(context or {}))
        return {"subject": subject, "body": body}

    # ------------------------------ #
    #   CREATE & QUEUE NOTIFICATION
    # ------------------------------ #
    def send_notification(
        self,
        recipient_id: str,
        recipient_type: str,
        channel: str,
        subject: str,
        body: str,
        template_name: Optional[str] = None,
        template_context: Optional[Dict[str, Any]] = None,
    ) -> Notification:

        chan_value = channel.value if isinstance(channel, Channel) else str(channel)

        # If template_name provided, fetch and render
        if template_name:
            tpl = self.repo.get_template_by_name(template_name)
            if tpl:
                rendered = self.render_template(tpl, template_context or {})
                subject = rendered.get("subject") or subject
                body = rendered.get("body") or body

        notif = Notification(
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            channel=chan_value,
            subject=subject,
            body=body,
        )

        saved = self.repo.create_notification(notif)

        # Queue asynchronous sending
        enqueue_send(saved.id)

        return saved

    # ------------------------------ #
    #   INTERNAL ACTUAL SEND LOGIC
    # ------------------------------ #
    def _perform_send(self, notification_id: int):
        notif = self.repo.get_notification(notification_id)
        if not notif:
            return

        resp = {"success": False, "response": "no_provider"}
        provider = None

        # ---------------- EMAIL ----------------
        if notif.channel == Channel.EMAIL.value:
            provider = self.sendgrid or DummyEmailProvider()
            resp = provider.send(
                to=notif.recipient_id,
                subject=notif.subject or "",
                body=notif.body or ""
            )

        # ---------------- SMS ----------------
        elif notif.channel == Channel.SMS.value and self.twilio:
            provider = self.twilio
            resp = provider.send(
                to=notif.recipient_id,
                subject=notif.subject or "",
                body=notif.body or ""
            )

        # ---------------- PUSH ----------------
        elif notif.channel == Channel.PUSH.value and self.fcm:
            provider = self.fcm
            resp = provider.send(
                to=notif.recipient_id,
                subject=notif.subject or "",
                body=notif.body or ""
            )

        # Log delivery attempt
        attempt = DeliveryAttempt(
            notification_id=notif.id,
            provider=resp.get("provider") if isinstance(resp, dict) else None,
            provider_response=str(resp),
            success=resp.get("success", False),
        )
        self.repo.create_attempt(attempt)

        # Mark as sent
        if attempt.success:
            notif.sent = True
            notif.sent_at = datetime.utcnow()
            self.repo.db.commit()
            self.repo.db.refresh(notif)

# Lazy wrapper to avoid circular import: import the real task only when used
def enqueue_send(*args, **kwargs):
    from app.tasks.notification_tasks import enqueue_send as _enqueue
    return _enqueue(*args, **kwargs)
