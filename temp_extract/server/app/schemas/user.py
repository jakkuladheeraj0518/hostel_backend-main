from pydantic import BaseModel, EmailStr, validator, ValidationError
from typing import Optional
from datetime import date, datetime
from .common import BaseSchema
from app.models.enums import UserType


class UserBase(BaseSchema):
    """Base user schema"""
    name: str
    email: EmailStr
    phone: str
    user_type: UserType = UserType.STUDENT


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class UserUpdate(BaseSchema):
    """User update schema"""
    name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    hostel_id: Optional[int] = None  # Changed from str to int to match database
    room_number: Optional[str] = None
    bed_number: Optional[str] = None
    profile_image: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    hostel_id: Optional[int] = None  # Changed from str to int to match database
    room_number: Optional[str] = None
    bed_number: Optional[str] = None
    check_in_date: Optional[date] = None
    profile_image: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseSchema):
    """User login schema"""
    email: EmailStr
    password: str


class UserPasswordChange(BaseSchema):
    """Password change schema"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserPasswordReset(BaseSchema):
    """Password reset schema"""
    email: EmailStr


class UserPasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema"""
    refresh_token: str


class TokenResponse(BaseSchema):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse