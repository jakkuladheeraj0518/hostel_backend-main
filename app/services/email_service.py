"""
Email service for sending OTP and notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import HTTPException, status
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails via SMTP"""
    
    def __init__(self):
        # Support either SMTP_* or EMAIL_* environment names (legacy/config mismatch)
        self.smtp_host = getattr(settings, 'SMTP_HOST', None) or getattr(settings, 'EMAIL_HOST', None)
        self.smtp_port = getattr(settings, 'SMTP_PORT', None) or getattr(settings, 'EMAIL_PORT', None)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None) or getattr(settings, 'EMAIL_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None) or getattr(settings, 'EMAIL_PASS', None)
        self.from_email = getattr(settings, 'SMTP_FROM_EMAIL', None) or getattr(settings, 'EMAIL_FROM', None) or self.smtp_username
        self.from_name = getattr(settings, 'SMTP_FROM_NAME', None) or getattr(settings, 'EMAIL_FROM_NAME', None) or settings.APP_NAME
        self.use_tls = getattr(settings, 'SMTP_USE_TLS', None) if hasattr(settings, 'SMTP_USE_TLS') else getattr(settings, 'EMAIL_USE_TLS', False)
        self.use_ssl = getattr(settings, 'SMTP_USE_SSL', None) if hasattr(settings, 'SMTP_USE_SSL') else getattr(settings, 'EMAIL_USE_SSL', False)
    
    def is_configured(self) -> bool:
        """Check if email service is configured"""
        return all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
            self.from_email
        ])
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        if not self.is_configured():
            logger.warning("Email service not configured. Email not sent.")
            # Provide masked SMTP config to help debugging without leaking secrets
            try:
                def _mask(v: str | None) -> str | None:
                    if not v:
                        return None
                    s = str(v)
                    if len(s) <= 4:
                        return "****"
                    return s[:2] + "*" * (len(s) - 4) + s[-2:]

                logger.info(
                    "Email configuration (masked): host=%s port=%s user=%s from=%s use_tls=%s use_ssl=%s",
                    _mask(self.smtp_host), _mask(self.smtp_port), _mask(self.smtp_username), _mask(self.from_email), self.use_tls, self.use_ssl
                )
            except Exception:
                pass
            if settings.DEBUG:
                logger.info(f"Would send email to {to_email}: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            # Login and send
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            if settings.DEBUG:
                logger.exception("Email sending error details:")
            return False
    
    def send_otp_email(self, to_email: str, otp_code: str, otp_type: str = "registration") -> bool:
        """Send OTP via email"""
        # OTP delivery has been disabled by administrator request.
        # Keep the method for backward compatibility but do not send OTPs.
        logger.info(f"OTP delivery disabled: would have sent OTP to {to_email} (type={otp_type})")
        if settings.DEBUG:
            logger.debug(f"OTP code for {to_email}: {otp_code}")
        # Return False to indicate no OTP was sent
        return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str = None, reset_code: str = None, user_name: str | None = None) -> bool:
        """Send password reset via email.

        Supports either a reset link (reset_token) or a numeric reset_code. If `reset_code` is provided,
        the email will contain the code and frontend URL; `user_name` is used in the code email template.
        """
        # Helper to generate HTML + text templates for a code flow
        def _generate_code_templates(user_name: str, reset_code: str, frontend_url: str):
            html = (
                f"<html><body style=\"font-family: Arial, sans-serif; padding: 20px;\">"
                f"<h2 style=\"color: #333;\">Password Reset Request</h2>"
                f"<p>Hello {user_name},</p>"
                f"<p>We received a request to reset your password.</p>"
                f"<div style=\"background: #f7f7f7; padding: 12px; border-radius: 6px; display: inline-block;\">"
                f"<strong style=\"font-size:18px;\">➡ {reset_code}</strong></div>"
                f"<p>Please enter this code on the password reset page: <a href=\"{frontend_url}\">{frontend_url}</a></p>"
                f"<p style=\"color:#666;\">Note: This code is valid for {settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes.</p>"
                f"<p style=\"color:#666;\">If you did not request a password reset, you can safely ignore this email.</p>"
                f"<p style=\"margin-top:12px;\">With regards,<br/>Support Team</p>"
                f"</body></html>"
            )

            text = (
                f"Hello {user_name}, "
                f"We received a request to reset your password. "
                f"Your password reset code is: ➡ {reset_code} "
                f"Please enter this code on the password reset page: {frontend_url} "
                f"Note: This code is valid for {settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes. "
                f"If you did not request a password reset, you can safely ignore this email. "
                f"With regards, Support Team"
            )

            return html, text

        # Build reset URL (token flow)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}" if reset_token else None
        subject = "Reset Your Password"

        # If reset_code is provided, prefer code+link email
        if reset_code:
            name = user_name or settings.APP_NAME
            # If a reset_token was provided as well, include it in the frontend URL
            frontend_reset_url = f"{settings.FRONTEND_URL}/reset-password"
            if reset_token:
                frontend_reset_url = f"{frontend_reset_url}?token={reset_token}"

            html_body, text_body = _generate_code_templates(name, reset_code, frontend_reset_url)
            return self.send_email(to_email, subject, html_body, text_body)

        # If only token provided -> link-only email
        if reset_url:
            html_body = (
                f"<html><body style=\"font-family: Arial, sans-serif; padding: 20px;\">"
                f"<h2 style=\"color: #333;\">Password Reset Request</h2>"
                f"<p>You requested to reset your password. Click the link below to reset it:</p>"
                f"<div style=\"text-align: center; margin: 20px 0;\">"
                f"<a href=\"{reset_url}\" style=\"background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;\">Reset Password</a></div>"
                f"<p>Or copy and paste this link into your browser:</p>"
                f"<p style=\"color: #666; word-break: break-all;\">{reset_url}</p>"
                f"<p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes.</p>"
                f"<p>If you didn't request this, please ignore this email.</p>"
                f"<hr style=\"margin: 20px 0; border: none; border-top: 1px solid #eee;\">"
                f"<p style=\"color: #666; font-size: 12px;\">This is an automated message, please do not reply.</p>"
                f"</body></html>"
            )

            text_body = f"Reset your password by clicking this link: {reset_url}\n\nThis link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes."
            return self.send_email(to_email, subject, html_body, text_body)

        logger.warning("send_password_reset_email called without token or code")
        return False

