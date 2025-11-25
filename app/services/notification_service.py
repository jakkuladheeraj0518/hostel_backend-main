from datetime import datetime
from typing import List, Optional, Dict, Any

from jinja2 import Template
from sqlalchemy.orm import Session

from app.integrations.sendgrid import send_email_sendgrid
from app.integrations.ses import send_email_ses
from app.integrations.twilio import send_sms_twilio
from app.integrations.sns import send_sms_sns
from app.integrations.firebase import send_push_fcm
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
)
from app.schemas.notification import (
    NotificationCreate,
    TemplateCreate,
    TemplateUpdate,
    BulkNotificationRequest,
)
from app.config import settings


class NotificationService:
    """
    Core notification engine:
    - Template management
    - Single notification send
    - Bulk + hierarchical routing (admin/supervisor/student)
    """

    # ========== Templates ==========

    @staticmethod
    def create_template(db: Session, data: TemplateCreate) -> NotificationTemplate:
        tmpl = NotificationTemplate(
            name=data.name,
            channel=data.channel.value,
            subject=data.subject,
            body=data.body,
        )
        db.add(tmpl)
        db.commit()
        db.refresh(tmpl)
        return tmpl

    @staticmethod
    def update_template(
        db: Session,
        template_id: int,
        data: TemplateUpdate,
    ) -> Optional[NotificationTemplate]:
        tmpl = db.query(NotificationTemplate).get(template_id)
        if not tmpl:
            return None
        if data.subject is not None:
            tmpl.subject = data.subject
        if data.body is not None:
            tmpl.body = data.body
        if data.is_active is not None:
            tmpl.is_active = 1 if data.is_active else 0
        tmpl.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(tmpl)
        return tmpl

    @staticmethod
    def get_template_by_name(
        db: Session,
        name: str,
    ) -> Optional[NotificationTemplate]:
        return (
            db.query(NotificationTemplate)
            .filter(NotificationTemplate.name == name)
            .first()
        )

    @staticmethod
    def list_templates(db: Session) -> List[NotificationTemplate]:
        return (
            db.query(NotificationTemplate)
            .order_by(NotificationTemplate.created_at.desc())
            .all()
        )

    # ========== Sending helpers ==========

    @staticmethod
    def _render_body(body: str, ctx: Optional[Dict[str, Any]]) -> str:
        if not ctx:
            return body
        return Template(body).render(**ctx)

    @staticmethod
    def _send_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
        # Choose provider via env
        if getattr(settings, "EMAIL_PROVIDER", "sendgrid") == "ses":
            return send_email_ses(recipient, subject, body)
        return send_email_sendgrid(recipient, subject, body)

    @staticmethod
    def _send_sms(recipient: str, body: str) -> Dict[str, Any]:
        # Choose provider via env
        if getattr(settings, "SMS_PROVIDER", "twilio") == "sns":
            return send_sms_sns(recipient, body)
        return send_sms_twilio(recipient, body)

    @staticmethod
    def _send_push(recipient: str, title: str, body: str) -> Dict[str, Any]:
        return send_push_fcm(recipient, title, body)

    # ========== Single send ==========

    @staticmethod
    def send_single(db: Session, payload: NotificationCreate) -> Notification:
        """
        Sends a single notification to one recipient.
        """
        template = None
        subject = payload.subject or ""
        body = payload.body or ""

        if payload.template_name:
            template = NotificationService.get_template_by_name(
                db, payload.template_name
            )
            if template and template.is_active:
                if not subject and template.subject:
                    subject = template.subject
                body = NotificationService._render_body(
                    template.body,
                    payload.template_data,
                )

        notif = Notification(
            hostel_id=payload.hostel_id,
            recipient_id=payload.recipient_id,
            recipient_type=payload.recipient_type,
            channel=payload.channel.value,
            subject=subject,
            body=body,
            priority=payload.priority.value,
            status=NotificationStatus.pending.value,
            template_id=template.id if template else None,
            template_data=payload.template_data,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        try:
            if payload.channel == NotificationChannel.email:
                provider_resp = NotificationService._send_email(
                    payload.recipient_id,
                    subject,
                    body,
                )
            elif payload.channel == NotificationChannel.sms:
                provider_resp = NotificationService._send_sms(
                    payload.recipient_id,
                    body,
                )
            elif payload.channel == NotificationChannel.push:
                provider_resp = NotificationService._send_push(
                    payload.recipient_id,
                    subject,
                    body,
                )
            else:
                provider_resp = {
                    "status_code": 400,
                    "error": "Unsupported channel",
                }

            status_code = provider_resp.get("status_code", 200)
            notif.provider_response = provider_resp

            if 200 <= status_code < 300:
                notif.status = NotificationStatus.sent.value
                notif.sent_at = datetime.utcnow()
            else:
                notif.status = NotificationStatus.failed.value
                notif.error_message = str(provider_resp)
        except Exception as exc:  # noqa: BLE001
            notif.status = NotificationStatus.failed.value
            notif.error_message = str(exc)

        db.commit()
        db.refresh(notif)
        return notif

    # ========== Routing / Bulk ==========

    @staticmethod
    def _get_role_recipients(
        db: Session,
        hostel_id: Optional[int],
        role: str,
    ) -> List[str]:
        """
        Helper for hierarchical routing.
        NOTE:
        - Adjust queries based on your actual user/admin/supervisor models.
        """
        if role == "admin":
            from app.models.admin_hostel_mapping import AdminHostelMapping
            from app.models.user import User

            q = (
                db.query(User.email)
                .join(AdminHostelMapping, AdminHostelMapping.admin_id == User.id)
            )
            if hostel_id:
                q = q.filter(AdminHostelMapping.hostel_id == hostel_id)
            return [row[0] for row in q.all() if row[0]]

        if role == "supervisor":
            from app.models.supervisor_assignment import SupervisorAssignment
            from app.models.user import User

            q = (
                db.query(User.email)
                .join(
                    SupervisorAssignment,
                    SupervisorAssignment.supervisor_id == User.id,
                )
            )
            if hostel_id:
                q = q.filter(SupervisorAssignment.hostel_id == hostel_id)
            return [row[0] for row in q.all() if row[0]]

        if role == "student":
            from app.models.student import Student

            q = db.query(Student.email)
            if hostel_id:
                q = q.filter(Student.hostel_id == hostel_id)
            return [row[0] for row in q.all() if row[0]]

        return []

    @staticmethod
    def send_bulk(db: Session, payload: BulkNotificationRequest) -> List[Notification]:
        """
        Bulk routing engine:
        - direct `recipients` list
        - plus / or role-based:
          * admins of hostel
          * supervisors of hostel
          * students of hostel
        """
        recipients: List[str] = []

        if payload.recipients:
            recipients.extend(payload.recipients)

        if payload.send_to_admins:
            recipients.extend(
                NotificationService._get_role_recipients(
                    db,
                    payload.hostel_id,
                    "admin",
                )
            )
        if payload.send_to_supervisors:
            recipients.extend(
                NotificationService._get_role_recipients(
                    db,
                    payload.hostel_id,
                    "supervisor",
                )
            )
        if payload.send_to_students:
            recipients.extend(
                NotificationService._get_role_recipients(
                    db,
                    payload.hostel_id,
                    "student",
                )
            )

        # dedupe
        recipients = sorted(set(recipients))

        sent_notifications: List[Notification] = []
        for r in recipients:
            single_payload = NotificationCreate(
                hostel_id=payload.hostel_id,
                recipient_id=r,
                recipient_type="auto_routed",
                channel=payload.channel,
                subject=payload.subject,
                body=payload.body,
                template_name=payload.template_name,
                template_data=payload.template_data,
                priority=payload.priority,
            )
            sent = NotificationService.send_single(db, single_payload)
            sent_notifications.append(sent)

        return sent_notifications

    # ========== Delivery tracking ==========

    @staticmethod
    def mark_delivered(
        db: Session,
        provider_message_id: str,
    ) -> Optional[Notification]:
        notif = (
            db.query(Notification)
            .filter(Notification.provider_message_id == provider_message_id)
            .first()
        )
        if not notif:
            return None
        notif.status = NotificationStatus.delivered.value
        notif.delivered_at = datetime.utcnow()
        db.commit()
        db.refresh(notif)
        return notif
