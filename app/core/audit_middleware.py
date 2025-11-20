"""
🧾 Audit trail middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from app.repositories.audit_repository import AuditRepository
from app.core.database import get_db


class AuditMiddleware(BaseHTTPMiddleware):
    """Log supervisor/admin actions to audit table"""
    
    async def dispatch(self, request: Request, call_next):
        # Only audit authenticated requests
        if not hasattr(request.state, "user_id"):
            return await call_next(request)
        
        # Only audit admin/supervisor actions
        user_role = getattr(request.state, "user_role", None)
        if user_role not in ["admin", "superadmin", "supervisor"]:
            return await call_next(request)
        
        # Log the request
        db = next(get_db())
        audit_repo = AuditRepository(db)
        
        try:
            audit_repo.create_audit_log(
                user_id=getattr(request.state, "user_id"),
                action=request.method,
                resource=request.url.path,
                hostel_id=getattr(request.state, "active_hostel_id", None),
                ip_address=request.client.host if request.client else None,
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            pass
        
        response = await call_next(request)
        return response

