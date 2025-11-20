"""
Utility helpers (decode JWT, extract role)
"""
from typing import Optional, Dict
from app.core.security import decode_token


def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode JWT token and return payload"""
    try:
        return decode_token(token)
    except Exception:
        return None


def extract_role_from_token(token: str) -> Optional[str]:
    """Extract role from JWT token"""
    payload = decode_jwt_token(token)
    if payload:
        return payload.get("role")
    return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from JWT token"""
    payload = decode_jwt_token(token)
    if payload:
        return payload.get("sub")
    return None


def extract_hostel_id_from_token(token: str) -> Optional[int]:
    """Extract hostel_id from JWT token"""
    payload = decode_jwt_token(token)
    if payload:
        return payload.get("hostel_id")
    return None

