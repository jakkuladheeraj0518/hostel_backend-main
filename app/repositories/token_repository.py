"""
Manage refresh tokens
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models.refresh_token import RefreshToken
from app.config import settings


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_token(self, user_id: int, token: str) -> RefreshToken:
        """Create refresh token"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_active=True
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token
    
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_active == True
        ).first()
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return False
        refresh_token.is_active = False
        self.db.commit()
        return True
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a user"""
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_active == True
        ).all()
        count = len(tokens)
        for token in tokens:
            token.is_active = False
        self.db.commit()
        return count
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        expired = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        ).all()
        count = len(expired)
        for token in expired:
            self.db.delete(token)
        self.db.commit()
        return count

