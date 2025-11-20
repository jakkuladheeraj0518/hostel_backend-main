"""
Role assignments, updates
"""
from sqlalchemy.orm import Session
from typing import List

from app.core.roles import Role, get_all_roles, can_manage_role
from app.repositories.user_repository import UserRepository


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_all_available_roles(self) -> List[str]:
        """Get all available roles"""
        return get_all_roles()
    
    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all users with a specific role"""
        users = self.user_repo.get_all(skip=skip, limit=limit)
        filtered = [u for u in users if u.role == role]
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "hostel_id": u.hostel_id
            }
            for u in filtered
        ]
    
    def can_assign_role(self, assigner_role: str, target_role: str) -> bool:
        """Check if assigner can assign target role"""
        return can_manage_role(assigner_role, target_role)

