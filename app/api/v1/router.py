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
from app.api.v1.supervisor import router as supervisor_module_router
from app.api.v1.super_admin import dashboard
from app.api.v1.student import complaints as student_complaints
from app.api.v1.supervisor import complaints as supervisor_complaints
from app.api.v1.admin import complaints as admin_complaints
from app.api.v1.visitor import search as visitor_search
from app.api.v1.super_admin import report as super_admin_reports
from app.api.v1.admin import reports as admin_reports
from app.api.v1.supervisor import reports as supervisor_reports
from app.api.v1.admin.rooms import router as rooms_router
from app.api.v1.admin.beds import router as beds_router
from app.api.v1.admin.students import router as students_router
from app.api.v1.admin.supervisors import router as supervisors_router
from app.api.v1.admin.comparison_router import router as comparison_router
# ⭐ Mess Menu & Announcement Imports
from app.api.v1.admin import mess_menu as admin_mess_menu
from app.api.v1.supervisor import mess_menu as supervisor_mess_menu
from app.api.v1.student import mess_menu as student_mess_menu

from app.api.v1.admin import announcement as admin_announcement
from app.api.v1.supervisor import announcement as supervisor_announcement
from app.api.v1.student import announcement as student_announcement

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

# Super Admin routes
api_router.include_router(super_admin_reports.router, prefix="/api/v1")

# Admin routes
api_router.include_router(admins.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_session.router, prefix="/admin", tags=["admin"])
api_router.include_router(audit.router, prefix="/admin", tags=["admin"])
api_router.include_router(permissions.router, prefix="/admin", tags=["admin"])
api_router.include_router(approvals.router, prefix="/admin", tags=["admin"])
api_router.include_router(rbac.router, prefix="/admin", tags=["admin"])
api_router.include_router(hostels.router, prefix="/admin", tags=["admin"])
api_router.include_router(dashboard.router)
api_router.include_router(supervisors_router)
api_router.include_router(students_router)
api_router.include_router(rooms_router)
api_router.include_router(beds_router)
# Comparison
api_router.include_router(comparison_router)
api_router.include_router(admin_mess_menu.router, prefix="/api/v1")
api_router.include_router(admin_announcement.router, prefix="/api/v1")
api_router.include_router(admin_complaints.router, prefix="/api/v1")
api_router.include_router(admin_reports.router, prefix="/api/v1")

# Note: audit endpoints are exposed under /admin/audit and /supervisor/audit
# Supervisor routes
api_router.include_router(supervisor_audit.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_permissions.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_approvals.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_complaints.router, prefix="/api/v1")
api_router.include_router(supervisor_reports.router, prefix="/api/v1")
api_router.include_router(supervisor_module_router, prefix="/supervisor", tags=["Supervisor Module"])
api_router.include_router(supervisor_mess_menu.router, prefix="/api/v1")
api_router.include_router(supervisor_announcement.router, prefix="/api/v1")
# Visitor routes have been disabled by admin request
api_router.include_router(visitor_search.router, prefix="/api/v1")
# Student routes
api_router.include_router(student_mess_menu.router, prefix="/api/v1")
api_router.include_router(student_announcement.router, prefix="/api/v1")
api_router.include_router(student_complaints.router, prefix="/api/v1")
# ...existing code...

