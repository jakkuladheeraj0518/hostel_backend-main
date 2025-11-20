import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

EMAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "your-email@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "app-password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@hostelpay.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

fast_mail = FastMail(EMAIL_CONFIG)

async def send_email_reminder(email: str, subject: str, body: str) -> bool:
    try:
        message = MessageSchema(subject=subject, recipients=[email], body=body, subtype="html")
        await fast_mail.send_message(message)
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False
