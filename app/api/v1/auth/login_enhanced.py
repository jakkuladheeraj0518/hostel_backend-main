"""
Enhanced login with email/phone and remember me
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_enhanced import UserLoginEnhanced
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login_user_enhanced(
    credentials: UserLoginEnhanced,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login with email/phone and optional remember me"""
    auth_service = AuthService(db)
    
    # Find user by email or phone
    user = None
    
    if '@' in credentials.email_or_phone:
        # Try email
        user = auth_service.user_repo.get_by_email(credentials.email_or_phone)
    else:
        # Try phone number
        users = auth_service.user_repo.get_all()
        for u in users:
            if u.phone_number and credentials.email_or_phone in u.phone_number:
                user = u
                break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password"
        )
    
    # Check if user has password (not social login only)
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses social login. Social login has been disabled by the administrator."
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not activated. Please verify your email/phone."
        )
    
    # Set remember me
    user.remember_me = credentials.remember_me
    db.commit()
    
    # Generate tokens with extended expiry for remember me
    expires_delta = None
    if credentials.remember_me:
        expires_delta = timedelta(days=30)  # 30 days for remember me
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "hostel_id": user.hostel_id, "email": user.email},
        expires_delta=expires_delta
    )
    
    # Refresh token always has longer expiry
    refresh_token_expiry = timedelta(days=30) if credentials.remember_me else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    # Store refresh token
    auth_service.token_repo.create_token(user.id, refresh_token)
    
    # If user asked to be remembered, set an HttpOnly cookie so other tabs can detect login
    # Cookie is set only for 'remember_me' to avoid implicit session cookies.
    response_payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 24 * 60 * 60 if credentials.remember_me else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }

    # Set cookie when remember_me is True so browser tabs can share authentication via HttpOnly cookie
    if credentials.remember_me:
        # Response object may be provided by FastAPI; if not, we won't set cookie
        try:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="lax",
                max_age=30 * 24 * 60 * 60
            )
        except Exception:
            # If response object is not available, just continue without cookie
            pass

    return response_payload

