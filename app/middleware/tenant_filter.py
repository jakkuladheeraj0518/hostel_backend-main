# """
# Filters data by hostel_id
# """
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from app.core.roles import Role
# from app.core.database import SessionLocal
# from app.repositories.session_repository import SessionRepository


# class TenantFilterMiddleware(BaseHTTPMiddleware):
#     """Filter queries by hostel_id for multi-tenant support"""
    
#     async def dispatch(self, request: Request, call_next):
#         # Superadmin can access all hostels
#         if hasattr(request.state, "user_role") and request.state.user_role == Role.SUPERADMIN:
#             request.state.bypass_tenant_filter = True
#             return await call_next(request)
        
#         # For admins, get active session hostel_id
#         active_hostel_id = None
#         if hasattr(request.state, "user_id") and hasattr(request.state, "user_role"):
#             user_id = request.state.user_id
#             user_role = request.state.user_role
            
#             # For admins, check active session
#             if user_role in [Role.ADMIN, Role.SUPERADMIN]:
#                 try:
#                     db = SessionLocal()
#                     session_repo = SessionRepository(db)
#                     active_session = session_repo.get_active_session(user_id)
#                     if active_session:
#                         active_hostel_id = active_session.hostel_id
#                     db.close()
#                 except Exception:
#                     pass
        
#         # Fallback to token hostel_id
#         if not active_hostel_id and hasattr(request.state, "hostel_id") and request.state.hostel_id:
#             active_hostel_id = request.state.hostel_id
        
#         # Allow query param override for session switching
#         hostel_id_param = request.query_params.get("hostel_id")
#         if hostel_id_param:
#             try:
#                 active_hostel_id = int(hostel_id_param)
#             except ValueError:
#                 pass
        
#         # Set active hostel_id in request state
#         if active_hostel_id:
#             request.state.active_hostel_id = active_hostel_id
        
#         return await call_next(request)



"""
Tenant filter middleware (function-style).
Sets request.state.active_hostel_id and request.state.bypass_tenant_filter.
"""

from fastapi import Request
from typing import Callable
from app.core.roles import Role
from app.core.database import SessionLocal
from app.repositories.session_repository import SessionRepository


PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi",
    "/uploads",
)


def _is_public(path: str) -> bool:
    # Keep tenant filtering for public routes minimal
    for p in PUBLIC_PREFIXES:
        if path.startswith(p):
            return True
    return False


async def tenant_filter_middleware(request: Request, call_next: Callable):
    path = request.url.path

    if _is_public(path):
        return await call_next(request)

    # Superadmin bypass
    if hasattr(request.state, "user_role") and request.state.user_role == Role.SUPERADMIN:
        request.state.bypass_tenant_filter = True
        return await call_next(request)

    active_hostel_id = None
    if hasattr(request.state, "user_id") and hasattr(request.state, "user_role"):
        user_id = request.state.user_id
        user_role = request.state.user_role

        if user_role in [Role.ADMIN, Role.SUPERADMIN]:
            try:
                db = SessionLocal()
                session_repo = SessionRepository(db)
                active_session = session_repo.get_active_session(user_id)
                if active_session:
                    active_hostel_id = active_session.hostel_id
            except Exception:
                # Don't fail request because of tenant lookup failure
                pass
            finally:
                try:
                    db.close()
                except Exception:
                    pass

    # Fallback to token hostel_id
    if not active_hostel_id and hasattr(request.state, "hostel_id") and request.state.hostel_id:
        active_hostel_id = request.state.hostel_id

    # Query param override
    hostel_id_param = request.query_params.get("hostel_id")
    if hostel_id_param:
        try:
            active_hostel_id = int(hostel_id_param)
        except ValueError:
            pass

    if active_hostel_id:
        request.state.active_hostel_id = active_hostel_id

    return await call_next(request)


