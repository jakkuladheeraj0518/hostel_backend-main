"""
Role-based access control logic
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.roles import Role, can_manage_role, get_role_level
from app.core.permissions import has_permission, get_role_permissions
from app.repositories.user_repository import UserRepository
from app.repositories.permission_repository import PermissionRepository
from app.schemas.rbac import RoleAssign, PermissionCheck


class RBACService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.permission_repo = PermissionRepository(db)
    
    def assign_role(self, assign_data: RoleAssign, assigner_role: str) -> dict:
        """Assign role to user (with permission check)"""
        # Check if assigner can manage this role
        if not can_manage_role(assigner_role, assign_data.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your role cannot assign {assign_data.role} role"
            )
        
        # Get user
        user = self.user_repo.get_by_id(assign_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user role
        from app.schemas.user import UserUpdate
        user_update = UserUpdate(role=assign_data.role)
        updated_user = self.user_repo.update(assign_data.user_id, user_update)
        
        return {
            "id": updated_user.id,
            "username": updated_user.username,
            "role": updated_user.role
        }
    
    def check_permission(self, check_data: PermissionCheck) -> bool:
        """Check if role has permission"""
        return has_permission(check_data.role, check_data.permission)
    
    def get_role_permissions_list(self, role: str) -> dict:
        """Get all permissions for a role"""
        permissions = get_role_permissions(role)
        return {
            "role": role,
            "permissions": list(permissions)
        }
    
    def validate_role_access(self, user_role: str, required_role: str) -> bool:
        """Validate if user role has access (hierarchy check)"""
        user_level = get_role_level(user_role)
        required_level = get_role_level(required_role)
        return user_level >= required_level

