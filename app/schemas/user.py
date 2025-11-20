"""
User creation/view schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    username: str
    full_name: Optional[str] = None
    role: str
    hostel_id: Optional[int] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for social login


class AdminCreate(UserBase):
    """Schema for creating admin users with password confirmation"""
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that confirm_password matches password"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password meets minimum requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    hostel_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

