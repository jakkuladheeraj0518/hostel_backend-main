import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json


def generate_unique_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID"""
    return secrets.token_urlsafe(length)[:length]


def generate_referral_code(length: int = 8) -> str:
    """Generate a referral code"""
    return secrets.token_urlsafe(length).upper()[:length]


def hash_string(text: str) -> str:
    """Hash a string using SHA-256"""
    return hashlib.sha256(text.encode()).hexdigest()


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.now().date()
    birth_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency"""
    return f"{currency}{amount:,.2f}"


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100


def get_month_date_range(year: int, month: int) -> tuple[datetime, datetime]:
    """Get start and end date of a month"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    return start_date, end_date


def parse_json_safely(json_string: Optional[str]) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string"""
    if not json_string:
        return None
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def serialize_to_json(data: Any) -> str:
    """Serialize data to JSON string"""
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return "{}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def is_valid_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in [t.lower() for t in allowed_types]


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    from math import radians, sin, cos, sqrt, atan2
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return r * c


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like phone numbers, emails"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def generate_otp(length: int = 6) -> str:
    """Generate OTP"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (Monday-Friday)"""
    return date.weekday() < 5


def get_next_business_day(date: datetime) -> datetime:
    """Get next business day"""
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day