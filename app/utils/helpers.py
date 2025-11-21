"""
Utility helpers for JWT decoding, extracting roles, user/hostel IDs,
and OTP expiry calculations.
"""

from typing import Optional, Dict
from datetime import datetime, timedelta

from app.core.security import decode_token
from app.config import settings


# =====================================================================
# 🔐 JWT DECODE HELPERS
# =====================================================================

def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode JWT token and return payload safely"""
    try:
        return decode_token(token)
    except Exception:
        return None


def extract_role_from_token(token: str) -> Optional[str]:
    """Extract role from JWT token"""
    payload = decode_jwt_token(token)
    return payload.get("role") if payload else None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from JWT token"""
    payload = decode_jwt_token(token)
    return payload.get("sub") if payload else None


def extract_hostel_id_from_token(token: str) -> Optional[int]:
    """Extract hostel_id from JWT token"""
    payload = decode_jwt_token(token)
    return payload.get("hostel_id") if payload else None


# =====================================================================
# 🔐 OTP EXPIRY HELPER
# =====================================================================

def otp_expiry_time(minutes: int = None) -> datetime:
    """Calculate OTP expiration time"""
    expiry_minutes = minutes or settings.OTP_EXPIRE_MINUTES
    return datetime.utcnow() + timedelta(minutes=expiry_minutes)
