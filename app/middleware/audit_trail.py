# """
# Logs requests to audit table
# """
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from app.core.roles import Role
# from app.repositories.audit_repository import AuditRepository
# from app.core.database import get_db


# class AuditTrailMiddleware(BaseHTTPMiddleware):
#     """Log admin/supervisor actions to audit table"""
    
#     async def dispatch(self, request: Request, call_next):
#         # Only audit authenticated requests
#         if not hasattr(request.state, "user_id"):
#             return await call_next(request)
        
#         # Only audit admin/supervisor/superadmin actions
#         user_role = getattr(request.state, "user_role", None)
#         if user_role not in [Role.ADMIN, Role.SUPERVISOR, Role.SUPERADMIN]:
#             return await call_next(request)
        
#         # Skip audit for GET requests (optional - can be enabled)
#         if request.method == "GET":
#             return await call_next(request)
        
#         # Log the request
#         try:
#             db = next(get_db())
#             audit_repo = AuditRepository(db)
#             audit_repo.create_audit_log(
#                 user_id=getattr(request.state, "user_id", None),
#                 action=request.method,
#                 resource=str(request.url.path),
#                 hostel_id=getattr(request.state, "active_hostel_id", None),
#                 ip_address=request.client.host if request.client else None,
#                 user_agent=request.headers.get("user-agent"),
#             )
#         except Exception as e:
#             # Log the exception for debugging
#             print(f"Audit logging failed: {e}")
#             # Don't fail request if audit logging fails
#             pass
        
#         response = await call_next(request)
#         return response


"""
Audit trail middleware (function-style).
Logs non-GET admin/supervisor actions. Failures are logged but do not block requests.
"""

from fastapi import Request
from typing import Callable
from app.core.roles import Role
from app.repositories.audit_repository import AuditRepository
from app.core.database import get_db
from starlette.responses import JSONResponse


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


async def audit_trail_middleware(request: Request, call_next: Callable):
    path = request.url.path

    if _is_public(path):
        return await call_next(request)

    if not hasattr(request.state, "user_id"):
        return await call_next(request)

    user_role = getattr(request.state, "user_role", None)
    if user_role not in [Role.ADMIN, Role.SUPERVISOR, Role.SUPERADMIN]:
        return await call_next(request)

    # Optionally skip GETs
    if request.method == "GET":
        return await call_next(request)

    # Non-blocking audit log
    try:
        db = next(get_db())
        audit_repo = AuditRepository(db)
        audit_repo.create_audit_log(
            user_id=getattr(request.state, "user_id", None),
            action=request.method,
            resource=str(request.url.path),
            hostel_id=getattr(request.state, "active_hostel_id", None),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as e:
        # Log the error (print for now)
        print(f"Audit logging failed: {e}")

    return await call_next(request)


