"""
JWT generation, refresh, role auth
"""
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.auth import UserLogin, UserRegister, Token
from app.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
    
    def register_user(self, user_data: UserRegister) -> dict:
        """Register a new user"""
        # Check if user already exists (email and phone_number optional)
        if user_data.email and self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if getattr(user_data, 'phone_number', None) and self.user_repo.get_by_phone_number(user_data.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        from app.schemas.user import UserCreate
        user_create = UserCreate(
            email=user_data.email,
            phone_number=getattr(user_data, 'phone_number', None),
            country_code=getattr(user_data, 'country_code', None),
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            hostel_id=None
        )
        user = self.user_repo.create(user_create)

        # By default, mark newly registered users as active and set verification flags
        changed = False
        if not user.is_active:
            user.is_active = True
            changed = True
        if user.email and not user.is_email_verified:
            user.is_email_verified = True
            changed = True
        if getattr(user, 'phone_number', None) and not user.is_phone_verified:
            user.is_phone_verified = True
            changed = True

        if changed:
            # commit the changes made to the user record
            self.db.commit()
            self.db.refresh(user)

        # OTP sending has been disabled per admin request; do not send OTPs on registration

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    
    def login(self, credentials: UserLogin) -> Token:
        """Authenticate user and generate tokens"""
        # Support login via email OR phone provided in `email_or_phone`
        identifier = credentials.email_or_phone
        user = None
        if identifier and '@' in identifier:
            # treat as email
            user = self.user_repo.get_by_email(identifier)
        else:
            # treat as phone (loose matching)
            user = self.user_repo.get_by_phone_number(identifier)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials"
            )
        
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Generate tokens
        # Per JWT best-practice and jose library expectations, ensure 'sub' is a string
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "hostel_id": user.hostel_id, "email": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role}
        )
        
        # Store refresh token
        self.token_repo.create_token(user.id, refresh_token)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token - decode without raising exception immediately
            from jose import jwt, JWTError
            try:
                payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            except JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid or expired refresh token: {str(e)}"
                )
            
            # Check token type
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type. Expected refresh token."
                )
            
            # Check if token exists in database
            token_record = self.token_repo.get_by_token(refresh_token)
            if not token_record:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not found or revoked"
                )
            
            # Check if token is expired (database check)
            from datetime import datetime, timezone
            if token_record.expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has expired"
                )
            
            # Get user
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            # Generate new access token
            # ensure subject is string when issuing a new access token
            access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role, "hostel_id": user.hostel_id, "email": user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error refreshing token: {str(e)}"
            )
    
    def logout(self, refresh_token: str) -> bool:
        """Revoke refresh token"""
        return self.token_repo.revoke_token(refresh_token)

