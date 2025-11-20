"""
JWT issue
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserLogin, Token

router = APIRouter()


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and receive JWT tokens"""
    auth_service = AuthService(db)
    return auth_service.login(credentials)

