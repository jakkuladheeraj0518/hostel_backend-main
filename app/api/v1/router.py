"""
Combines all routers
"""
from fastapi import APIRouter

from app.api.v1.auth import (
    login, refresh, roles,
    login_enhanced, password_reset, password_strength, me
)
from app.api.v1.admin import session as admin_session, audit, permissions, rbac, hostels, approvals, admins
from app.api.v1.supervisor import audit as supervisor_audit, permissions as supervisor_permissions, approvals as supervisor_approvals
from app.api.v1.super_admin import dashboard
# ...existing code...

api_router = APIRouter()



# Enhanced auth routes
api_router.include_router(login_enhanced.router, prefix="/auth", tags=["auth"])
# Auth routes
api_router.include_router(refresh.router, prefix="/auth", tags=["auth"])
api_router.include_router(roles.router, prefix="/auth", tags=["auth"])
api_router.include_router(password_reset.router, prefix="/auth", tags=["auth"])
api_router.include_router(password_strength.router, prefix="/auth", tags=["auth"])
api_router.include_router(me.router, prefix="/auth", tags=["auth"])

# Admin routes
api_router.include_router(admins.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_session.router, prefix="/admin", tags=["admin"])
api_router.include_router(audit.router, prefix="/admin", tags=["admin"])
api_router.include_router(permissions.router, prefix="/admin", tags=["admin"])
api_router.include_router(approvals.router, prefix="/admin", tags=["admin"])
api_router.include_router(rbac.router, prefix="/admin", tags=["admin"])
api_router.include_router(hostels.router, prefix="/admin", tags=["admin"])
api_router.include_router(dashboard.router)

# Note: audit endpoints are exposed under /admin/audit and /supervisor/audit
# Supervisor routes
api_router.include_router(supervisor_audit.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_permissions.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_approvals.router, prefix="/supervisor", tags=["supervisor"])

# Visitor routes have been disabled by admin request

# ...existing code...

