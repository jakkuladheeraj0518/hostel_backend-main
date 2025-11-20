"""
Custom exceptions (AccessDenied, InvalidHostel)
"""
from fastapi import HTTPException, status


class AccessDeniedException(HTTPException):
    """Raised when user doesn't have permission"""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InvalidHostelException(HTTPException):
    """Raised when hostel_id is invalid or user doesn't have access"""
    def __init__(self, detail: str = "Invalid hostel or access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class RoleNotFoundException(HTTPException):
    """Raised when role doesn't exist"""
    def __init__(self, detail: str = "Role not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class SessionNotFoundException(HTTPException):
    """Raised when session doesn't exist"""
    def __init__(self, detail: str = "Session not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

