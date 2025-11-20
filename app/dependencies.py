"""
Dependency injection setup.
Shared dependencies (DB, Auth, RBAC, Header-based identity)
"""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from typing import Generator


# Service dependency factories
def get_mess_menu_service(db: Session = Depends(get_db)):
    """Provide MessMenuService wired with a DB session."""
    from app.services.mess_menu_service import MessMenuService

    return MessMenuService(db)


# ---------------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------------

def get_db_session(db: Session = Depends(get_db)) -> Session:
    """Get database session"""
    return db


# ---------------------------------------------------------
# BASIC AUTH PLACEHOLDERS (No real authentication yet)
# ---------------------------------------------------------

def get_current_user():
    """
    Placeholder for user authentication.
    Replace with JWT or session-based authentication later.
    """
    return {"user_id": 1, "role": "admin"}


def require_admin():
    """Placeholder for admin role verification"""
    return get_current_user()


def require_supervisor():
    """Placeholder for supervisor role verification"""
    return get_current_user()


def require_student():
    """Placeholder for student role verification"""
    return get_current_user()


# ---------------------------------------------------------
# USER STATUS CHECKING (When real User model is used)
# ---------------------------------------------------------

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Validate active user"""
    if hasattr(current_user, "is_active") and not current_user.is_active:
        raise ValueError("User is not active")
    return current_user


# ---------------------------------------------------------
# HEADER-BASED AUTH (Used when API Gateway sets headers)
# ---------------------------------------------------------

async def get_current_user_email(request: Request) -> str:
    """Extract email injected by proxy/header"""
    email = request.headers.get("X-User-Email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing X-User-Email header")
    return email


async def get_current_user_name(request: Request) -> str:
    """Extract name injected by proxy/header"""
    name = request.headers.get("X-User-Name")
    if not name:
        raise HTTPException(status_code=400, detail="Missing X-User-Name header")
    return name
