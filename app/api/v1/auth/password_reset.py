"""
Password reset endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.password_reset_service import PasswordResetService
from app.schemas.auth_enhanced import (
    PasswordResetRequest,
    PasswordResetVerify,
    PasswordResetComplete
)

router = APIRouter()


@router.post("/forgot-password", response_model=dict, status_code=status.HTTP_200_OK)
async def forgot_password(
    request: PasswordResetRequest,
    debug: bool = False,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    reset_service = PasswordResetService(db)
    return reset_service.create_reset_request(request.email_or_phone, include_debug=debug)


@router.post("/verify-reset-code", response_model=dict, status_code=status.HTTP_200_OK)
async def verify_reset_code(
    request: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """Verify password reset code or token"""
    reset_service = PasswordResetService(db)
    return reset_service.verify_reset_code(
        request.email_or_phone,
        request.reset_code,
        request.reset_token
    )


@router.post("/reset-password", response_model=dict, status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetComplete,
    db: Session = Depends(get_db)
):
    """Complete password reset"""
    reset_service = PasswordResetService(db)
    return reset_service.reset_password(
        reset_token=request.reset_token,
        reset_code=request.reset_code,
        email_or_phone=request.email_or_phone,
        new_password=request.new_password
    )

