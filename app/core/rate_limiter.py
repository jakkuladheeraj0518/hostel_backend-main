"""
Rate limiting middleware for API endpoints
Protects against brute force attacks and API abuse
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],  # Default limit for all endpoints
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
    strategy="fixed-window"
)

# Custom rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors
    Returns a JSON response with retry information
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc),
            "retry_after": exc.detail if hasattr(exc, 'detail') else "60 seconds"
        },
        headers={
            "Retry-After": "60"
        }
    )

# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    "auth_login": "5/minute",           # Login attempts
    "auth_register": "3/minute",        # Registration attempts
    "password_reset": "3/hour",         # Password reset requests
    "review_submission": "10/hour",     # Review submissions
    "complaint_submission": "20/hour",  # Complaint submissions
    "maintenance_request": "30/hour",   # Maintenance requests
    "leave_application": "10/hour",     # Leave applications
    "file_upload": "50/hour",           # File uploads
    "search": "100/hour",               # Search queries
    "public_api": "200/hour",           # Public API endpoints
    "admin_operations": "500/hour",     # Admin operations
}

def get_rate_limit(endpoint_type: str) -> str:
    """Get rate limit for specific endpoint type"""
    return RATE_LIMITS.get(endpoint_type, "100/hour")

# Decorator for applying rate limits
def rate_limit(limit: str):
    """
    Decorator to apply rate limiting to endpoints
    
    Usage:
        @rate_limit("5/minute")
        @router.post("/login")
        def login(...):
            ...
    """
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator
