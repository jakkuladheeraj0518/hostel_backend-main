"""
Insert/view audit logs
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogFilter


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_audit_log(
        self,
        user_id: int,
        action: str,
        resource: str,
        hostel_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        """Create audit log entry"""
        audit_log = AuditLog(
            user_id=user_id,
            hostel_id=hostel_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def get_by_id(self, audit_id: int) -> Optional[AuditLog]:
        """Get audit log by ID"""
        return self.db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditLogFilter] = None
    ) -> List[AuditLog]:
        """Get audit logs with optional filters"""
        query = self.db.query(AuditLog)
        
        if filters:
            if filters.user_id:
                query = query.filter(AuditLog.user_id == filters.user_id)
            if filters.hostel_id:
                query = query.filter(AuditLog.hostel_id == filters.hostel_id)
            if filters.action:
                query = query.filter(AuditLog.action == filters.action)
            if filters.start_date:
                query = query.filter(AuditLog.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(AuditLog.created_at <= filters.end_date)
        
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_hostel(self, hostel_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific hostel"""
        return self.db.query(AuditLog).filter(
            AuditLog.hostel_id == hostel_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_target(self, target_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Search audit logs by a target identifier.

        This searches both the `resource` column and the `details` JSON/text blob
        for occurrences of the target_id. The search is a simple SQL LIKE match
        to keep implementation lightweight.
        """
        like_pattern = f"%{target_id}%"
        return self.db.query(AuditLog).filter(
            (AuditLog.resource.ilike(like_pattern)) | (AuditLog.details.ilike(like_pattern))
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

