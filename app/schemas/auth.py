"""
Login, register, token schemas
"""
from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional


class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    username: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "visitor"


class UserLogin(BaseModel):
    # Allow login by a single identifier (email OR phone) supplied as `email_or_phone`.
    # `remember_me` is optional and can be used by the client to request longer-lived tokens.
    email_or_phone: Optional[str] = None
    password: str
    remember_me: Optional[bool] = False

    @model_validator(mode='after')
    def validate_identifier(self):
        if not self.email_or_phone:
            raise ValueError('Either email or phone must be provided in `email_or_phone`')
        return self


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

