"""
Active hostel sessions
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.session_context import SessionContext
from app.schemas.session import SessionContextCreate


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_session(self, user_id: int) -> Optional[SessionContext]:
        """Get active session for user"""
        return self.db.query(SessionContext).filter(
            SessionContext.user_id == user_id,
            SessionContext.is_active == True
        ).first()
    
    def get_all_sessions(self, user_id: int) -> List[SessionContext]:
        """Get all sessions for user"""
        return self.db.query(SessionContext).filter(
            SessionContext.user_id == user_id
        ).order_by(SessionContext.updated_at.desc()).all()
    
    def create_session(self, user_id: int, hostel_id: int) -> SessionContext:
        """Create or activate session"""
        # Deactivate existing sessions
        existing = self.db.query(SessionContext).filter(
            SessionContext.user_id == user_id,
            SessionContext.is_active == True
        ).all()
        for session in existing:
            session.is_active = False
        
        # Check if session already exists
        existing_session = self.db.query(SessionContext).filter(
            SessionContext.user_id == user_id,
            SessionContext.hostel_id == hostel_id
        ).first()
        
        if existing_session:
            existing_session.is_active = True
            self.db.commit()
            self.db.refresh(existing_session)
            return existing_session
        
        # Create new session
        new_session = SessionContext(user_id=user_id, hostel_id=hostel_id, is_active=True)
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session
    
    def deactivate_session(self, user_id: int, session_id: int) -> bool:
        """Deactivate a session"""
        session = self.db.query(SessionContext).filter(
            SessionContext.id == session_id,
            SessionContext.user_id == user_id
        ).first()
        if not session:
            return False
        session.is_active = False
        self.db.commit()
        return True

