from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode

class OTPVerify(BaseModel):
    otp_code: str

class OTPResend(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# <<<< Make sure this exists
class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
