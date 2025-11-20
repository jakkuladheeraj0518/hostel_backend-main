"""
Session context (active hostel)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from app.repositories.session_repository import SessionRepository
from app.repositories.hostel_repository import HostelRepository
from app.services.tenant_service import TenantService
from app.schemas.session import SwitchSessionRequest, SessionContextResponse
from app.core.roles import Role


class SessionService:
    def __init__(self, db: Session):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.hostel_repo = HostelRepository(db)
        self.tenant_service = TenantService(db)
    
    def switch_session(self, user_id: int, user_role: str, request: SwitchSessionRequest) -> SessionContextResponse:
        """Switch active hostel session"""
        # Validate hostel access
        self.tenant_service.validate_hostel_access(user_id, user_role, request.hostel_id)
        
        # Create/activate session
        session = self.session_repo.create_session(user_id, request.hostel_id)
        
        return SessionContextResponse(
            id=session.id,
            user_id=session.user_id,
            hostel_id=session.hostel_id,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    
    def get_active_session(self, user_id: int) -> Optional[SessionContextResponse]:
        """Get active session for user"""
        session = self.session_repo.get_active_session(user_id)
        if not session:
            return None
        
        return SessionContextResponse(
            id=session.id,
            user_id=session.user_id,
            hostel_id=session.hostel_id,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    
    def get_recent_sessions(self, user_id: int, limit: int = 5) -> List[SessionContextResponse]:
        """Get recently accessed hostels"""
        sessions = self.session_repo.get_all_sessions(user_id)
        recent = sessions[:limit]
        
        return [
            SessionContextResponse(
                id=s.id,
                user_id=s.user_id,
                hostel_id=s.hostel_id,
                is_active=s.is_active,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in recent
        ]
    
    def deactivate_session(self, user_id: int, session_id: int) -> bool:
        """Deactivate a session"""
        return self.session_repo.deactivate_session(user_id, session_id)

