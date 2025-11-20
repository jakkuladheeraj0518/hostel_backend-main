"""
Security utilities:
- Safe bcrypt wrapper (handles >72 byte passwords)
- Hash / verify
- JWT access + refresh tokens
- Get current user
"""

import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.core.database import get_db


# ======================
#  BCRYPT SAFE CONTEXT
# ======================

class BcryptContext:
    """
    Custom bcrypt wrapper that safely handles long passwords.
    Anything >72 bytes is pre-hashed with SHA256 and tagged as `sha256$<digest>`.
    """

    def __init__(self):
        self._bcrypt = bcrypt

    def _prepare(self, raw: str) -> bytes:
        raw_bytes = raw.encode("utf-8")
        if len(raw_bytes) > 72:
            digest = hashlib.sha256(raw_bytes).hexdigest()
            return f"sha256${digest}".encode("utf-8")
        return raw_bytes

    def hash(self, password: str) -> str:
        prepared = self._prepare(password)
        hashed = self._bcrypt.hashpw(prepared, self._bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            prepared = self._prepare(plain)
            return self._bcrypt.checkpw(prepared, hashed.encode("utf-8"))
        except Exception:
            return False


pwd_context = BcryptContext()


# ======================
#  PASSWORD API
# ======================

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ======================
#  JWT TOKENS
# ======================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="HTTPBearer",
    auto_error=False
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ======================
#  CURRENT USER
# ======================

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    # Fallback: read from cookie
    if not token:
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            token = cookie_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token. Provide Authorization header or access_token cookie.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
        raw_sub = payload.get("sub")

        if raw_sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = int(raw_sub)

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
