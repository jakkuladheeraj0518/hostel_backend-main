"""
Audit log creation/viewing
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.roles import Role
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogFilter, AuditLogResponse


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)
    
    def create_audit_log(
        self,
        user_id: int,
        action: str,
        resource: str,
        hostel_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None
    ) -> AuditLogResponse:
        """Create audit log entry"""
        audit_log = self.audit_repo.create_audit_log(
            user_id=user_id,
            action=action,
            resource=resource,
            hostel_id=hostel_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        return AuditLogResponse(
            id=audit_log.id,
            user_id=audit_log.user_id,
            hostel_id=audit_log.hostel_id,
            action=audit_log.action,
            resource=audit_log.resource,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            details=audit_log.details,
            created_at=audit_log.created_at
        )
    
    def get_audit_logs(
        self,
        viewer_role: str,
        viewer_user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditLogFilter] = None
    ) -> List[AuditLogResponse]:
        """Get audit logs (with role-based filtering)"""
        # Only admin/supervisor/superadmin can view audit logs
        if viewer_role not in [Role.ADMIN, Role.SUPERVISOR, Role.SUPERADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view audit logs"
            )
        
        # Superadmin can see all logs
        if viewer_role == Role.SUPERADMIN:
            logs = self.audit_repo.get_all(skip=skip, limit=limit, filters=filters)
        else:
            # Admin/supervisor can only see logs for their hostel(s)
            if filters and filters.hostel_id:
                logs = self.audit_repo.get_all(skip=skip, limit=limit, filters=filters)
            else:
                # Get user's hostel and filter
                from app.repositories.user_repository import UserRepository
                user_repo = UserRepository(self.db)
                user = user_repo.get_by_id(viewer_user_id)
                if user and user.hostel_id:
                    if filters:
                        filters.hostel_id = user.hostel_id
                    else:
                        filters = AuditLogFilter(hostel_id=user.hostel_id)
                    logs = self.audit_repo.get_all(skip=skip, limit=limit, filters=filters)
                else:
                    logs = []
        
        return [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                hostel_id=log.hostel_id,
                action=log.action,
                resource=log.resource,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                details=log.details,
                created_at=log.created_at
            )
            for log in logs
        ]
    
    def get_user_audit_logs(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLogResponse]:
        """Get audit logs for a specific user"""
        logs = self.audit_repo.get_by_user(user_id, skip=skip, limit=limit)
        return [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                hostel_id=log.hostel_id,
                action=log.action,
                resource=log.resource,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                details=log.details,
                created_at=log.created_at
            )
            for log in logs
        ]

    def get_target_audit_logs(self, target_id: str, skip: int = 0, limit: int = 100) -> List[AuditLogResponse]:
        """Search audit logs by a target identifier present in resource or details."""
        logs = self.audit_repo.get_by_target(target_id, skip=skip, limit=limit)
        return [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                hostel_id=log.hostel_id,
                action=log.action,
                resource=log.resource,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                details=log.details,
                created_at=log.created_at
            )
            for log in logs
        ]

