"""
Supervisor Authentication
Special login endpoint for supervisors with hostel context
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.roles import Role
from app.models.user import User
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/supervisor/login")
async def supervisor_login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Supervisor-specific login endpoint
    Returns access token with hostel context
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is supervisor, admin, or superadmin - ROLE-BASED AUTHENTICATION
    allowed_roles = [Role.SUPERVISOR.value, Role.ADMIN.value, Role.SUPERADMIN.value]
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Supervisor access required. Your role: {user.role}"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "hostel_id": str(user.hostel_id) if user.hostel_id else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    }
