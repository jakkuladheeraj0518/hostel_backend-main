from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token
)
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserPasswordReset, UserPasswordResetConfirm, UserPasswordChange,
    RefreshTokenRequest
)
from app.schemas.common import MessageResponse
from app.models.user import User
from app.config import settings

router = APIRouter()
security = HTTPBearer()


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify user from JWT token"""
    try:
        token = credentials.credentials
        return verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.get("/check-availability")
async def check_availability(
    email: str = None,
    phone: str = None,
    db: Session = Depends(get_db)
):
    """Check if email or phone is available for registration"""
    
    if not email and not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either email or phone to check"
        )
    
    result = {"available": True, "conflicts": []}
    
    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            result["available"] = False
            result["conflicts"].append("email")
    
    if phone:
        existing_phone = db.query(User).filter(User.phone == phone).first()
        if existing_phone:
            result["available"] = False
            result["conflicts"].append("phone")
    
    return result


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    
    if existing_email and existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email and phone already exists"
        )
    elif existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    elif existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    if len(user_data.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long (maximum 72 bytes)"
        )
    
    # Create new user
    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        user_type=user_data.user_type,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return tokens"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # For supervisors, include hostel context in token
    token_data = {
        "sub": user.id, 
        "email": user.email, 
        "user_type": user.user_type.value
    }
    
    # Add hostel context for supervisors
    if user.user_type.value == "supervisor" and user.hostel_id:
        token_data["hostel_id"] = user.hostel_id
        token_data["hostel_context"] = True
    
    # Create tokens
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )


@router.post("/supervisor/login", response_model=TokenResponse)
async def supervisor_login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Supervisor-specific login with enhanced hostel context"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify user is a supervisor
    if user.user_type.value not in ["supervisor", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required"
        )
    
    # Create enhanced token with supervisor context
    token_data = {
        "sub": user.id,
        "email": user.email,
        "user_type": user.user_type.value,
        "hostel_id": user.hostel_id,
        "hostel_context": True,
        "supervisor_session": True
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email, "supervisor_session": True}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    
    try:
        payload = verify_token(request.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "user_type": user.user_type.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user
        )
        
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: UserPasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not
        return MessageResponse(message="If the email exists, a reset link has been sent")
    
    # Generate reset token (implement email sending logic here)
    from app.core.security import generate_reset_token
    reset_token = generate_reset_token()
    
    user.password_reset_token = reset_token
    # Set expiry (implement datetime logic)
    db.commit()
    
    # TODO: Send email with reset token
    
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: UserPasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    
    user = db.query(User).filter(User.password_reset_token == request.token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.password_hash = get_password_hash(request.new_password)
    user.password_reset_token = None
    db.commit()
    
    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: UserPasswordChange,
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    user = db.query(User).filter(User.id == current_user["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return MessageResponse(message="Password changed successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    
    user = db.query(User).filter(User.id == current_user["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user