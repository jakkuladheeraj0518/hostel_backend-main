"""
Password strength checker endpoint
"""
from fastapi import APIRouter, Query
from app.utils.password_strength import check_password_strength

router = APIRouter()


@router.get("/password-strength", response_model=dict)
async def check_password(
    password: str = Query(..., description="Password to check")
):
    """Check password strength"""
    return check_password_strength(password)

