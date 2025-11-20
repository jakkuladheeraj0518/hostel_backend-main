"""
Helper utilities (decode JWT, etc.)
"""
from typing import Optional, Dict
from app.core.security import decode_token


def extract_user_info_from_token(token: str) -> Optional[Dict]:
    """Extract user information from JWT token"""
    try:
        payload = decode_token(token)
        return {
            "user_id": payload.get("sub"),
            "role": payload.get("role"),
            "hostel_id": payload.get("hostel_id"),
            "email": payload.get("email"),
        }
    except Exception:
        return None


def get_hostel_id_from_request(request) -> Optional[int]:
    """Extract hostel_id from request state"""
    return getattr(request.state, "active_hostel_id", None) or getattr(request.state, "hostel_id", None)

