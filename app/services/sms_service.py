"""
SMS service for sending OTP and notifications via Twilio
"""
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Try to import Twilio, but make it optional
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. Install with: pip install twilio")


class SMSService:
    """SMS service for sending SMS via Twilio"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        # support both TWILIO_FROM_NUMBER (current) and legacy TWILIO_PHONE_NUMBER
        self.phone_number = getattr(settings, 'TWILIO_FROM_NUMBER', None) or getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        self.client = None
        
        if TWILIO_AVAILABLE and self.is_configured():
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Error initializing Twilio client: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if SMS service is configured"""
        return all([
            self.account_sid,
            self.auth_token,
            self.phone_number
        ])
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not TWILIO_AVAILABLE:
            logger.warning("Twilio not installed. SMS not sent.")
            if settings.DEBUG:
                logger.info(f"Would send SMS to {to_phone}: {message}")
            return False
        
        if not self.is_configured():
            logger.warning("SMS service not configured. SMS not sent.")
            if settings.DEBUG:
                logger.info(f"Would send SMS to {to_phone}: {message}")
            return False
        
        try:
            # Format phone number (ensure it starts with +)
            if not to_phone.startswith('+'):
                to_phone = f"+{to_phone.lstrip('+')}"
            
            # Send SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully to {to_phone}. SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {str(e)}")
            if settings.DEBUG:
                logger.exception("SMS sending error details:")
            return False
    
    def send_otp_sms(self, to_phone: str, otp_code: str, otp_type: str = "registration") -> bool:
        """Send OTP via SMS"""
        # OTP delivery has been disabled by administrator request.
        logger.info(f"OTP delivery disabled: would have sent SMS to {to_phone} (type={otp_type})")
        if settings.DEBUG:
            logger.debug(f"OTP code for {to_phone}: {otp_code}")
        return False
    
    def send_password_reset_sms(self, to_phone: str, reset_code: str) -> bool:
        """Send password reset code via SMS"""
        message = f"Your {settings.APP_NAME} password reset code is: {reset_code}. Valid for {settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES} minutes. Do not share this code."
        return self.send_sms(to_phone, message)

