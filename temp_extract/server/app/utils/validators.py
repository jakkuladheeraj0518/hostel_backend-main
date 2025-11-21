import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid format (10-15 digits, optionally starting with +)
    pattern = r'^\+?[1-9]\d{9,14}$'
    return bool(re.match(pattern, cleaned))


def validate_email_address(email: str) -> bool:
    """Validate email address"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """Validate password strength and return errors"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def validate_pincode(pincode: str) -> bool:
    """Validate pincode format"""
    # Basic validation for 5-6 digit pincode
    return bool(re.match(r'^\d{5,6}$', pincode))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = text.strip()
    
    # Remove multiple consecutive spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_room_number(room_number: str) -> bool:
    """Validate room number format"""
    # Allow alphanumeric room numbers (e.g., "101", "A-101", "B2-205")
    pattern = r'^[A-Za-z0-9\-]{1,10}$'
    return bool(re.match(pattern, room_number))


def validate_amount(amount: float) -> bool:
    """Validate monetary amount"""
    return amount > 0 and amount <= 999999.99


def validate_rating(rating: float) -> bool:
    """Validate rating value (1-5 scale)"""
    return 1.0 <= rating <= 5.0