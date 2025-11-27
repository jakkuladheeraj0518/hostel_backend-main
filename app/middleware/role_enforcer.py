# """
# Role enforcement (RBAC)
# """
# from fastapi import Request, HTTPException, status
# from starlette.middleware.base import BaseHTTPMiddleware
# from app.core.roles import Role
# from app.core.exceptions import AccessDeniedException


# class RoleEnforcerMiddleware(BaseHTTPMiddleware):
#     """Enforce role-based access control"""
    
#     async def dispatch(self, request: Request, call_next):
#         # Skip for public endpoints
#         if not hasattr(request.state, "user_role"):
#             return await call_next(request)
        
#         user_role = request.state.user_role
        
#         # Check admin endpoints
#         if request.url.path.startswith("/api/v1/admin"):
#             if user_role not in [Role.ADMIN, Role.SUPERADMIN]:
#                 raise AccessDeniedException("Admin access required")
        
#         # Check supervisor endpoints
#         if request.url.path.startswith("/api/v1/supervisor"):
#             if user_role != Role.SUPERVISOR:
#                 raise AccessDeniedException("Supervisor access required")
        
#         return await call_next(request)


"""
Role enforcement middleware (function-style).
Returns 403 JSON response for access violations (does not raise).
"""

from fastapi import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from typing import Callable
from app.core.roles import Role


PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi",
    "/uploads",
)


def _is_public(path: str) -> bool:
    for p in PUBLIC_PREFIXES:
        if path.startswith(p):
            return True
    return False


async def role_enforcer_middleware(request: Request, call_next: Callable):
    path = request.url.path

    if _is_public(path):
        return await call_next(request)

    # If unauthenticated, skip enforcement (authentication middleware should run earlier)
    if not hasattr(request.state, "user_role"):
        return await call_next(request)

    user_role = request.state.user_role

    # Admin endpoints
    if path.startswith("/api/v1/admin"):
        if user_role not in [Role.ADMIN, Role.SUPERADMIN]:
            return JSONResponse({"detail": "Admin access required"}, status_code=HTTP_403_FORBIDDEN)

    # Supervisor endpoints
    if path.startswith("/api/v1/supervisor"):
        if user_role != Role.SUPERVISOR:
            return JSONResponse({"detail": "Supervisor access required"}, status_code=HTTP_403_FORBIDDEN)

    return await call_next(request)
