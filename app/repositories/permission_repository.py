"""
Permission lookups
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.permission import Permission, RolePermission


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def get_all(self) -> List[Permission]:
        """Get all permissions"""
        return self.db.query(Permission).filter(Permission.is_active == True).all()
    
    def get_role_permissions(self, role: str) -> List[Permission]:
        """Get all permissions for a role"""
        role_perms = self.db.query(RolePermission).filter(
            RolePermission.role == role
        ).all()
        permission_ids = [rp.permission_id for rp in role_perms]
        return self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    
    def assign_permission_to_role(self, role: str, permission_id: int) -> RolePermission:
        """Assign permission to role"""
        # Check if already assigned
        existing = self.db.query(RolePermission).filter(
            RolePermission.role == role,
            RolePermission.permission_id == permission_id
        ).first()
        if existing:
            return existing
        
        role_perm = RolePermission(role=role, permission_id=permission_id)
        self.db.add(role_perm)
        self.db.commit()
        self.db.refresh(role_perm)
        return role_perm
    
    def remove_permission_from_role(self, role: str, permission_id: int) -> bool:
        """Remove permission from role"""
        role_perm = self.db.query(RolePermission).filter(
            RolePermission.role == role,
            RolePermission.permission_id == permission_id
        ).first()
        if not role_perm:
            return False
        self.db.delete(role_perm)
        self.db.commit()
        return True

