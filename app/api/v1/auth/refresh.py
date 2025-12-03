"""
Refresh tokens
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import RefreshTokenRequest, RefreshTokenResponse

router = APIRouter()




@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token_data: RefreshTokenRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Logout by revoking the provided refresh token and clearing auth cookie if present."""
    auth_service = AuthService(db)
    revoked = auth_service.logout(token_data.refresh_token)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found or already revoked")

    # Clear remember-me cookie if set
    try:
        response.delete_cookie("access_token")
    except Exception:
        pass

    return {"message": "Logged out successfully"}

