"""
Password reset service
"""
import secrets
import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
import logging

from app.models.password_reset import PasswordResetToken
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash
from app.config import settings
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)


class PasswordResetService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_expiry_minutes = settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES
        self.reset_code_length = settings.PASSWORD_RESET_CODE_LENGTH
    
    def generate_reset_token(self) -> str:
        """Generate secure reset token"""
        return secrets.token_urlsafe(32)
    
    def generate_reset_code(self) -> str:
        """Generate 6-digit reset code for SMS"""
        return ''.join(random.choices(string.digits, k=self.reset_code_length))
    
    def create_reset_request(self, email_or_phone: str, include_debug: bool = False) -> dict:
        """Create password reset request"""
        # Find user by email or phone
        user = None
        
        # Try email first
        if '@' in email_or_phone:
            user = self.user_repo.get_by_email(email_or_phone)
        else:
            # Try phone number exact match or username match first
            user = self.user_repo.get_by_phone_number(email_or_phone)
            if not user:
                # Try username (some users may provide username instead of email)
                user = self.user_repo.get_by_username(email_or_phone)
                if user:
                    # If a username was provided, switch the target to the user's email
                    email_or_phone = user.email or email_or_phone
            # Fallback: try fuzzy phone substring search across users
            if not user:
                users = self.user_repo.get_all()
                for u in users:
                    if u.phone_number and email_or_phone in u.phone_number:
                        user = u
                        break
        
        if not user:
            # Don't reveal if user exists (security best practice)
            # But still send a generic notification to the supplied address/phone
            # (User requested: always send a notification on forgot-password)
            email_service = EmailService()
            sms_service = SMSService()

            generic_message_text = (
                "A password reset was requested for this address. "
                "If you initiated this request, follow the instructions on the password reset page. "
                "If you did not request this, you can safely ignore this message."
            )

            try:
                if '@' in email_or_phone:
                    subject = "Password reset requested"
                    # Simple HTML and text bodies
                    html_body = f"<p>{generic_message_text}</p><p>If needed, visit: {settings.FRONTEND_URL}/reset-password</p>"
                    text_body = generic_message_text + f"\nVisit: {settings.FRONTEND_URL}/reset-password"
                    email_service.send_email(email_or_phone, subject, html_body, text_body)
                else:
                    # send generic SMS notification (do not include codes)
                    sms_service.send_sms(email_or_phone, generic_message_text)
            except Exception:
                # Swallow exceptions to avoid revealing implementation details
                logger.exception("Error sending generic password reset notification")

            return {
                "message": "If an account exists with this email/phone, you will receive a password reset link/code shortly."
            }
        
        # Generate reset token and code
        reset_token = self.generate_reset_token()
        reset_code = self.generate_reset_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.token_expiry_minutes)
        
        # Create reset token record
        reset_token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            reset_code=reset_code,
            expires_at=expires_at,
            is_used=False
        )
        
        self.db.add(reset_token_record)
        self.db.commit()
        self.db.refresh(reset_token_record)
        
        # Send email with reset link and SMS with reset code
        email_service = EmailService()
        sms_service = SMSService()

        # Always attempt to email the reset code/link when we have the user's email
        display_name = user.full_name or user.username or user.email
        try:
            if user.email:
                # pass both reset_code and reset_token so the email can include both
                email_service.send_password_reset_email(user.email, reset_token=reset_token, reset_code=reset_code, user_name=display_name)
                # Log the tokenized frontend URL and the single-line email text for easy verification
                frontend_reset_url = f"{settings.FRONTEND_URL}/reset-password"
                if reset_token:
                    frontend_reset_url = f"{frontend_reset_url}?token={reset_token}"
                logger.info(f"Password reset link for {user.email}: {frontend_reset_url}")
                single_line_email = (
                    f"Hello {display_name}, We received a request to reset your password. "
                    f"Your password reset code is: ➡ {reset_code} "
                    f"Please enter this code on the password reset page: {frontend_reset_url} "
                    f"Note: This code is valid for {self.token_expiry_minutes} minutes. "
                    f"If you did not request a password reset, you can safely ignore this email. With regards, Support Team"
                )
                logger.info(single_line_email)
        except Exception:
            logger.exception("Error sending password reset email; continuing")

        # If request was via phone (no '@'), still send SMS
        if '@' in email_or_phone:
            # request came by email; we've already attempted email delivery
            pass
        else:
            # Send SMS with reset code
            try:
                sms_service.send_password_reset_sms(email_or_phone, reset_code)
            except Exception:
                logger.exception("Error sending password reset SMS; continuing")
        
        # Log in debug mode
        # Log the reset (always helpful in debug). The actual email send may be skipped if email not configured.
        if settings.DEBUG:
            if '@' in email_or_phone:
                logger.info(f"Password reset link for {email_or_phone}: {settings.FRONTEND_URL}/reset-password?token={reset_token}")
            else:
                logger.info(f"Password reset code for {email_or_phone}: {reset_code}")

        # Return a generic message; include debug details only when explicitly requested
        response = {
            "message": "If an account exists with this email/phone, you will receive a password reset link/code shortly.",
            "expires_in_minutes": self.token_expiry_minutes
        }

        if settings.DEBUG and include_debug:
            # include safe debug details for development/testing only when requested
            response["debug"] = {
                "reset_token": reset_token,
                "reset_code": reset_code,
                "reset_url": f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            }

        return response
    
    def verify_reset_code(self, email_or_phone: str, reset_code: Optional[str] = None, reset_token: Optional[str] = None) -> dict:
        """Verify reset code or token"""
        if not reset_code and not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either reset_code or reset_token must be provided"
            )
        
        # Find user
        user = None
        if '@' in email_or_phone:
            user = self.user_repo.get_by_email(email_or_phone)
        else:
            users = self.user_repo.get_all()
            for u in users:
                if u.phone_number and email_or_phone in u.phone_number:
                    user = u
                    break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Find reset token
        query = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        )
        
        if reset_token:
            query = query.filter(PasswordResetToken.token == reset_token)
        elif reset_code:
            query = query.filter(PasswordResetToken.reset_code == reset_code)
        
        reset_token_record = query.first()
        
        if not reset_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset code or token"
            )
        
        # Check expiration
        if reset_token_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link/code has expired. Please request a new one."
            )
        
        return {
            "valid": True,
            "token": reset_token_record.token,
            "user_id": user.id
        }
    
    def reset_password(
        self,
        reset_token: Optional[str] = None,
        reset_code: Optional[str] = None,
        email_or_phone: str = None,
        new_password: str = None
    ) -> dict:
        """Complete password reset"""
        # Verify reset token/code first
        verification = self.verify_reset_code(email_or_phone, reset_code, reset_token)
        user_id = verification["user_id"]
        
        # Get reset token record
        query = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.is_used == False
        )
        
        if reset_token:
            query = query.filter(PasswordResetToken.token == reset_token)
        elif reset_code:
            query = query.filter(PasswordResetToken.reset_code == reset_code)
        
        reset_token_record = query.first()
        
        if not reset_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token or code"
            )
        
        # Update password
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        # Mark token as used
        reset_token_record.is_used = True
        reset_token_record.used_at = datetime.now(timezone.utc)
        self.db.commit()
        
        return {
            "message": "Password reset successfully. Please login with your new password."
        }

