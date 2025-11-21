"""
JWT generation, refresh, role auth, password hashing, OTP, email & SMS utilities
Merged into one complete authentication module.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import bcrypt
import random
import ssl
import smtplib
from email.mime.text import MIMEText
from jose import jwt

from app.core.security import decode_token     # Keeping decode_token if used elsewhere
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.auth import UserLogin, UserRegister, Token
from app.config import settings


# ============================================================
# 🔐 PASSWORD HASHING & VERIFICATION
# ============================================================

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


# ============================================================
# 🔐 JWT GENERATION
# ============================================================

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create short-lived access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    """Create long-lived refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# 🔐 OTP GENERATION & SENDING
# ============================================================

def generate_otp() -> str:
    return f"{random.randint(100000, 999999):06d}"


async def send_otp_email(email: str, otp_code: str) -> bool:
    subject = "Your OTP Code"
    # FIX: Use EXPIRY
    body = (
        f"Hello,\n\nYour OTP code is: {otp_code}\n"
        f"This OTP is valid for {settings.OTP_EXPIRY_MINUTES} minutes.\n\nRegards,\nYour Company"
    )
    msg = MIMEText(body)
    msg["Subject"] = subject
    sender_email = settings.EMAIL_FROM or settings.EMAIL_USER
    msg["From"] = sender_email
    msg["To"] = email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False


async def send_otp_sms(phone: str, otp_code: str) -> bool:
    print(f"Sending SMS OTP to {phone}: {otp_code}")
    return True


def otp_expiry_time(minutes: int = None) -> datetime:
    """Calculate OTP expiration time"""
    # FIX: Use EXPIRY, not EXPIRE
    expiry_minutes = minutes or settings.OTP_EXPIRY_MINUTES
    return datetime.utcnow() + timedelta(minutes=expiry_minutes)


# ============================================================
# 🔐 AUTH SERVICE (MAIN LOGIC)
# ============================================================

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    # --------------------------------------------------------
    # USER REGISTRATION
    # --------------------------------------------------------
    def register_user(self, user_data: UserRegister) -> dict:

        # Prevent duplicates
        if user_data.email and self.user_repo.get_by_email(user_data.email):
            raise HTTPException(400, "Email already registered")

        if getattr(user_data, "phone_number", None) and \
                self.user_repo.get_by_phone_number(user_data.phone_number):
            raise HTTPException(400, "Phone already registered")

        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(400, "Username already taken")

        # Create user
        from app.schemas.user import UserCreate

        user_create = UserCreate(
            email=user_data.email,
            phone_number=getattr(user_data, "phone_number", None),
            country_code=getattr(user_data, "country_code", None),
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            hostel_id=None
        )

        user = self.user_repo.create(user_create)

        # Auto-verify
        changed = False
        if not user.is_active:
            user.is_active = True
            changed = True
        if user.email and not user.is_email_verified:
            user.is_email_verified = True
            changed = True
        if getattr(user, "phone_number", None) and not user.is_phone_verified:
            user.is_phone_verified = True
            changed = True

        if changed:
            self.db.commit()
            self.db.refresh(user)

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------
    def login(self, credentials: UserLogin) -> Token:

        identifier = credentials.email_or_phone
        user = None

        if identifier and "@" in identifier:
            user = self.user_repo.get_by_email(identifier)
        else:
            user = self.user_repo.get_by_phone_number(identifier)

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(401, "Incorrect credentials")

        if not user.is_active:
            raise HTTPException(403, "User account is inactive")

        # JWT Tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "hostel_id": user.hostel_id, "email": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role}
        )

        # Store refresh token
        self.token_repo.create_token(user.id, refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    # --------------------------------------------------------
    # REFRESH ACCESS TOKEN
    # --------------------------------------------------------
    def refresh_access_token(self, refresh_token: str) -> dict:

        from jose import JWTError

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError as e:
            raise HTTPException(401, f"Invalid or expired refresh token: {str(e)}")

        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type. Expected refresh token.")

        token_record = self.token_repo.get_by_token(refresh_token)
        if not token_record:
            raise HTTPException(401, "Refresh token revoked or not found")

        if token_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(401, "Refresh token expired")

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(401, "User not found")

        if not user.is_active:
            raise HTTPException(403, "User account is inactive")

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "hostel_id": user.hostel_id, "email": user.email}
        )

        return {"access_token": access_token, "token_type": "bearer"}

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------
    def logout(self, refresh_token: str) -> bool:
        return self.token_repo.revoke_token(refresh_token)
