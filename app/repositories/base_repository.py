"""
Base repository with automatic hostel filtering
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer
from app.core.roles import Role


class BaseRepository:
    """Base repository with automatic tenant filtering"""
    
    def __init__(self, db: Session, user_role: Optional[str] = None, active_hostel_id: Optional[int] = None, user_hostel_ids: Optional[List[int]] = None):
        self.db = db
        self.user_role = user_role
        self.active_hostel_id = active_hostel_id
        self.user_hostel_ids = user_hostel_ids
    
    def _apply_hostel_filter(self, query, hostel_column: Column):
        """Apply hostel filter to query based on user role and access"""
        # Superadmin bypass
        if self.user_role == Role.SUPERADMIN:
            return query
        
        # If active_hostel_id is set, filter by it
        if self.active_hostel_id:
            return query.filter(hostel_column == self.active_hostel_id)
        
        # If user has assigned hostels (admin), filter by those
        if self.user_hostel_ids:
            return query.filter(hostel_column.in_(self.user_hostel_ids))
        
        # No filter applied (shouldn't happen in normal flow)
        return query
    
    def _validate_hostel_access(self, hostel_id: int) -> bool:
        """Validate if user has access to a specific hostel"""
        # Superadmin has access to all
        if self.user_role == Role.SUPERADMIN:
            return True
        
        # Check if hostel_id is in user's accessible hostels
        if self.user_hostel_ids:
            return hostel_id in self.user_hostel_ids
        
        # Check active hostel
        if self.active_hostel_id:
            return hostel_id == self.active_hostel_id
        
        return False

