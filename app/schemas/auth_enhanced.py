"""
Enhanced authentication schemas with OTP, social login, password reset
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re





class UserLoginEnhanced(BaseModel):
    """Enhanced login with email/phone"""
    email_or_phone: str  # Can be email or phone
    password: str
    remember_me: bool = False


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email_or_phone: str  # Can be email or phone


class PasswordResetVerify(BaseModel):
    """Verify reset code/token"""
    email_or_phone: str
    reset_code: Optional[str] = None  # For SMS
    reset_token: Optional[str] = None  # For email link


class PasswordResetComplete(BaseModel):
    """Complete password reset"""
    reset_token: Optional[str] = None
    reset_code: Optional[str] = None
    email_or_phone: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v




class PasswordStrengthResponse(BaseModel):
    """Password strength indicator"""
    strength: str  # 'weak', 'medium', 'strong'
    score: int  # 0-100
    feedback: list[str]  # Suggestions for improvement


