"""
Role enforcement (RBAC)
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.roles import Role
from app.core.exceptions import AccessDeniedException


class RoleEnforcerMiddleware(BaseHTTPMiddleware):
    """Enforce role-based access control"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        if not hasattr(request.state, "user_role"):
            return await call_next(request)
        
        user_role = request.state.user_role
        
        # Check admin endpoints
        if request.url.path.startswith("/api/v1/admin"):
            if user_role not in [Role.ADMIN, Role.SUPERADMIN]:
                raise AccessDeniedException("Admin access required")
        
        # Check supervisor endpoints
        if request.url.path.startswith("/api/v1/supervisor"):
            if user_role != Role.SUPERVISOR:
                raise AccessDeniedException("Supervisor access required")
        
        return await call_next(request)

