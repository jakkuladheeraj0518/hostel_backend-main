"""
Comprehensive audit logging system for tracking sensitive operations
Logs all critical actions for security and compliance
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from app.models.base import Base

logger = logging.getLogger(__name__)

class AuditAction(str, Enum):
    """Enumeration of auditable actions"""
    # Authentication
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    
    # User Management
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_STATUS_CHANGED = "USER_STATUS_CHANGED"
    
    # Hostel Management
    HOSTEL_CREATED = "HOSTEL_CREATED"
    HOSTEL_UPDATED = "HOSTEL_UPDATED"
    HOSTEL_DELETED = "HOSTEL_DELETED"
    HOSTEL_ASSIGNED = "HOSTEL_ASSIGNED"
    
    # Review Moderation
    REVIEW_APPROVED = "REVIEW_APPROVED"
    REVIEW_REJECTED = "REVIEW_REJECTED"
    REVIEW_DELETED = "REVIEW_DELETED"
    REVIEW_FLAGGED_SPAM = "REVIEW_FLAGGED_SPAM"
    
    # Maintenance
    MAINTENANCE_APPROVED = "MAINTENANCE_APPROVED"
    MAINTENANCE_REJECTED = "MAINTENANCE_REJECTED"
    HIGH_VALUE_MAINTENANCE = "HIGH_VALUE_MAINTENANCE"
    MAINTENANCE_COMPLETED = "MAINTENANCE_COMPLETED"
    
    # Leave Management
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    
    # Financial
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_REFUNDED = "PAYMENT_REFUNDED"
    COST_ADDED = "COST_ADDED"
    
    # Security
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    
    # Data Access
    SENSITIVE_DATA_ACCESSED = "SENSITIVE_DATA_ACCESSED"
    BULK_EXPORT = "BULK_EXPORT"
    DATA_MODIFIED = "DATA_MODIFIED"

class AuditLog(Base):
    """Database model for audit logs"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(32), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="SUCCESS")
    error_message = Column(Text, nullable=True)

class AuditLogger:
    """Audit logging service"""
    
    @staticmethod
    def log(
        db: Session,
        action: AuditAction,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None
    ):
        """
        Log an audit event to database and application logs
        
        Args:
            db: Database session
            action: Type of action performed
            user_id: ID of user performing action
            user_email: Email of user
            user_role: Role of user
            ip_address: IP address of request
            user_agent: User agent string
            resource_type: Type of resource affected (e.g., 'user', 'hostel', 'review')
            resource_id: ID of affected resource
            details: Additional details as JSON
            status: SUCCESS or FAILURE
            error_message: Error message if status is FAILURE
        """
        try:
            # Create audit log entry
            audit_entry = AuditLog(
                action=action.value,
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                status=status,
                error_message=error_message
            )
            
            db.add(audit_entry)
            db.commit()
            
            # Also log to application logger
            log_message = f"AUDIT: {action.value} | User: {user_email or 'Anonymous'} ({user_role or 'N/A'}) | Resource: {resource_type}:{resource_id} | Status: {status}"
            if status == "SUCCESS":
                logger.info(log_message)
            else:
                logger.warning(f"{log_message} | Error: {error_message}")
                
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            # Don't raise exception - audit logging should not break application flow
    
    @staticmethod
    def log_authentication(
        db: Session,
        action: AuditAction,
        email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log authentication events"""
        AuditLogger.log(
            db=db,
            action=action,
            user_email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="authentication",
            status="SUCCESS" if success else "FAILURE",
            error_message=error_message
        )
    
    @staticmethod
    def log_user_management(
        db: Session,
        action: AuditAction,
        actor_id: int,
        actor_email: str,
        actor_role: str,
        target_user_id: int,
        details: Dict[str, Any],
        ip_address: str
    ):
        """Log user management actions"""
        AuditLogger.log(
            db=db,
            action=action,
            user_id=actor_id,
            user_email=actor_email,
            user_role=actor_role,
            ip_address=ip_address,
            resource_type="user",
            resource_id=target_user_id,
            details=details
        )
    
    @staticmethod
    def log_review_moderation(
        db: Session,
        action: AuditAction,
        moderator_id: int,
        moderator_email: str,
        moderator_role: str,
        review_id: int,
        reason: Optional[str],
        ip_address: str
    ):
        """Log review moderation actions"""
        AuditLogger.log(
            db=db,
            action=action,
            user_id=moderator_id,
            user_email=moderator_email,
            user_role=moderator_role,
            ip_address=ip_address,
            resource_type="review",
            resource_id=review_id,
            details={"reason": reason} if reason else None
        )
    
    @staticmethod
    def log_maintenance_approval(
        db: Session,
        action: AuditAction,
        approver_id: int,
        approver_email: str,
        approver_role: str,
        maintenance_id: int,
        cost: float,
        ip_address: str
    ):
        """Log maintenance approval actions"""
        AuditLogger.log(
            db=db,
            action=action,
            user_id=approver_id,
            user_email=approver_email,
            user_role=approver_role,
            ip_address=ip_address,
            resource_type="maintenance",
            resource_id=maintenance_id,
            details={"cost": cost, "requires_approval": cost >= 1000}
        )
    
    @staticmethod
    def log_security_event(
        db: Session,
        action: AuditAction,
        user_id: Optional[int],
        user_email: Optional[str],
        ip_address: str,
        details: Dict[str, Any]
    ):
        """Log security-related events"""
        AuditLogger.log(
            db=db,
            action=action,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            resource_type="security",
            details=details,
            status="FAILURE"
        )

# Helper function to get client IP from request
def get_client_ip(request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# Helper function to get user agent from request
def get_user_agent(request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")
