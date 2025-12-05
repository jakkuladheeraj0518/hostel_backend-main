"""
Session switching APIs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.roles import Role
from app.api.deps import role_required, get_current_active_user
from app.models.user import User
from app.services.session_service import SessionService
from app.schemas.session import SwitchSessionRequest, SessionContextResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.post("/session/switch", response_model=SessionContextResponse, status_code=status.HTTP_200_OK)
async def switch_session(
    request: SwitchSessionRequest,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Switch active hostel session"""
    session_service = SessionService(db)
    return session_service.switch_session(current_user.id, current_user.role, request)


@router.post("/session/set-active-hostel", response_model=SessionContextResponse, status_code=status.HTTP_200_OK)
async def set_active_hostel(
    request: SwitchSessionRequest,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Set or activate the user's active hostel (alias for switch)."""
    session_service = SessionService(db)
    return session_service.switch_session(current_user.id, current_user.role, request)




@router.get("/session/active", response_model=SessionContextResponse, status_code=status.HTTP_200_OK)
async def get_active_session(
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get active session"""
    session_service = SessionService(db)
    session = session_service.get_active_session(current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )
    return session





@router.get("/session/recent", response_model=List[SessionContextResponse], status_code=status.HTTP_200_OK)
async def get_recent_sessions(
    limit: int = 5,
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Get recently accessed hostels"""
    session_service = SessionService(db)
    return session_service.get_recent_sessions(current_user.id, limit)




@router.post("/session/clear", status_code=status.HTTP_200_OK)
async def clear_session(
    session_id: Optional[int] = Body(None, embed=True, description="Optional session id to clear; if omitted, clears the active session"),
    current_user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Clear/deactivate a session. If session_id omitted, deactivate the active session.

    Returns a JSON object with a success message and the cleared `session_id`.
    """
    session_service = SessionService(db)
    # If no session_id provided, get active session
    if session_id is None:
        active = session_service.get_active_session(current_user.id)
        if not active:
            # nothing to clear
            return {"message": "No active session to clear", "session_id": None}
        session_id = active.id

    ok = session_service.deactivate_session(current_user.id, session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")

    return {"message": "Session cleared", "session_id": session_id}

