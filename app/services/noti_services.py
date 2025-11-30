from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.noti_models import EmailProvider, EmailStatus, EmailTemplate
from app.utils.noti_utils import render_template
from app.repositories.noti_repository import EmailTemplateRepository, EmailLogRepository
import os
import boto3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridProvider:
    def __init__(self):
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing SENDGRID_API_KEY")
        self.client = SendGridAPIClient(api_key)

    def send(self, recipient, subject, html, text):
        mail = Mail(
            from_email=os.getenv("FROM_EMAIL", "noreply@example.com"),
            to_emails=recipient,
            subject=subject,
            html_content=html,
            plain_text_content=text
        )
        res = self.client.send(mail)
        # response headers may contain X-Message-Id or other identifiers
        return (res.headers.get("X-Message-Id") if hasattr(res, 'headers') else None)

class AwsSesProvider:
    def __init__(self):
        self.client = boto3.client(
            "ses",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    def send(self, recipient, subject, html, text):
        body = {"Html": {"Data": html}}
        if text:
            body["Text"] = {"Data": text}
        res = self.client.send_email(
            Source=os.getenv("FROM_EMAIL", "noreply@example.com"),
            Destination={"ToAddresses": [recipient]},
            Message={"Subject": {"Data": subject}, "Body": body},
        )
        return res.get("MessageId")

class EmailService:

    @staticmethod
    def get_provider_instance(provider: EmailProvider):
        if provider == EmailProvider.sendgrid:
            return SendGridProvider()
        return AwsSesProvider()

    @staticmethod
    def send_email(db: Session, request):
        # request is Pydantic model; access attributes
        html = request.html_content
        text = request.text_content
        subject = request.subject
        template_id = None

        if request.template_name:
            template = EmailTemplateRepository.get(db, request.template_name) if False else None
            # We will fetch template directly by name (avoid adding a new repo method)
            template = db.query(EmailTemplate).filter(
                EmailTemplate.name == request.template_name,
                EmailTemplate.is_active == True
            ).first()
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            template_id = template.id
            html = render_template(template.html_content, request.variables or {})
            if template.text_content:
                text = render_template(template.text_content, request.variables or {})
            subject = render_template(template.subject, request.variables or {})

        log = EmailLogRepository.create_log(db, {
            "recipient": request.recipient,
            "subject": subject,
            "template_id": template_id,
            "provider": request.provider,
            "status": EmailStatus.pending
        })

        provider_inst = EmailService.get_provider_instance(request.provider)

        try:
            message_id = provider_inst.send(request.recipient, subject, html, text)
            EmailLogRepository.update_log(db, log, {
                "status": EmailStatus.SENT,
                "message_id": message_id,
                "sent_at": datetime.utcnow()
            })
        except Exception as e:
            EmailLogRepository.update_log(db, log, {
                "status": EmailStatus.FAILED,
                "error_message": str(e)
            })

        return log
