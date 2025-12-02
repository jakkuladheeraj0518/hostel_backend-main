from fastapi import APIRouter

#=============================================================
#vistor registration
#=============================================================

#=============================================================
#login
from app.api.v1.auth import (
    login, refresh, roles,
    login_enhanced, password_reset, password_strength, me
)
#=============================================================

#=============================================================
#superadmin dashboard
from app.api.v1.admin import (
    session as admin_session,
    audit,
    permissions,
    rbac,
    hostels as admin_hostels,
    approvals,
    admins as admin_admins,
)
 
# Super-admin module routers (alias to avoid name collisions with admin package)
from app.api.v1.super_admin import (
    admins as super_admin_admins,
    reports as super_admin_reports,
    hostels as super_admin_hostels,
    dashboard as super_admin_dashboard,
    subscription as super_admin_subscription,
    analytics as super_admin_analytics,
    shift_coordination as super_admin_shift_coordination,
)
 
#=============================================================

#=============================================================
#admin dashboard 
from app.api.v1.admin.rooms import router as rooms_router
from app.api.v1.admin.beds import router as beds_router
from app.api.v1.admin.students import router as students_router
from app.api.v1.admin.supervisors import router as supervisors_router
from app.api.v1.admin.comparison_router import router as comparison_router

from app.api.v1.admin import complaints as admin_complaints
from app.api.v1.admin import reports as admin_reports

from app.api.v1.admin import mess_menu as admin_mess_menu
from app.api.v1.admin import announcement as admin_announcement


from app.api.v1.admin import (
    fee_structure_configuration,
    payment_routers as payment_routes,
    transactions,
)
from app.api.v1.admin import invoices, transactions, receipts, refunds
from app.api.v1.admin.ledger_routes import router as ledger_router
from app.api.v1.admin.reminder_configs import router as reminder_config_router
from app.api.v1.admin.reminder_templates import router as reminder_template_router

#=============================================================

#=============================================================
#supervisor dashboard

from app.api.v1.supervisor import audit as supervisor_audit, permissions as supervisor_permissions, approvals as supervisor_approvals
from app.api.v1.supervisor import router as supervisor_module_router
from app.api.v1.supervisor import complaints as supervisor_complaints
from app.api.v1.supervisor import reports as supervisor_reports

from app.api.v1.supervisor import mess_menu as supervisor_mess_menu
from app.api.v1.supervisor import announcement as supervisor_announcement
#=============================================================

#=============================================================
#student dashboard
from app.api.v1.student import complaints as student_complaints
from app.api.v1.visitor import search as visitor_search

from app.api.v1.student import mess_menu as student_mess_menu
from app.api.v1.student import announcement as student_announcement
#=============================================================

#=============================================================
#visitor dasboard
#=============================================================
api_router = APIRouter()
#=============================================================
#vistor registration
#=============================================================

#=============================================================
#login
# Enhanced auth routes
api_router.include_router(login_enhanced.router, prefix="/auth", tags=["auth"])
# Auth routes
api_router.include_router(refresh.router, prefix="/auth", tags=["auth"])
api_router.include_router(roles.router, prefix="/auth", tags=["auth"])
api_router.include_router(password_reset.router, prefix="/auth", tags=["auth"])
api_router.include_router(password_strength.router, prefix="/auth", tags=["auth"])
api_router.include_router(me.router, prefix="/auth", tags=["auth"])
#=============================================================

#=============================================================
#superadmin dashboard
#superadmin dashboard
api_router.include_router(admin_admins.router, prefix="/admin", tags=["admin"])
api_router.include_router(permissions.router, prefix="/admin", tags=["admin"])
api_router.include_router(rbac.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_hostels.router, prefix="/admin", tags=["admin"])
 
# Include super-admin routers as they define their own prefixes/tags internally.
api_router.include_router(super_admin_hostels.router)
api_router.include_router(super_admin_dashboard.router)
api_router.include_router(super_admin_admins.router)
api_router.include_router(super_admin_subscription.router)
api_router.include_router(super_admin_reports.router)
api_router.include_router(super_admin_analytics.router)
api_router.include_router(super_admin_shift_coordination.router)

#=============================================================

#=============================================================
#admin dashboard 
api_router.include_router(admin_session.router, prefix="/hostel_admin", tags=["hostel_admin"])
api_router.include_router(audit.router, prefix="/hostel_admin", tags=["hostel_admin"])
api_router.include_router(approvals.router, prefix="/hostel_admin", tags=["hostel_admin"])

api_router.include_router(supervisors_router)
api_router.include_router(students_router)
api_router.include_router(rooms_router)
api_router.include_router(beds_router)
# Comparison
api_router.include_router(comparison_router)

api_router.include_router(admin_complaints.router, prefix="/api/v1")
api_router.include_router(admin_reports.router, prefix="/api/v1")

api_router.include_router(admin_mess_menu.router, prefix="/api/v1")
api_router.include_router(admin_announcement.router, prefix="/api/v1")

#fee and payment
api_router.include_router(fee_structure_configuration.router)
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(payment_routes.router)
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
api_router.include_router(refunds.router, prefix="/refunds", tags=["Refunds"])
api_router.include_router(ledger_router)
api_router.include_router(reminder_config_router)
api_router.include_router(reminder_template_router)
#=============================================================

#=============================================================
#supervisor dashboard
api_router.include_router(supervisor_audit.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_permissions.router, prefix="/supervisor", tags=["supervisor"])
api_router.include_router(supervisor_approvals.router, prefix="/supervisor", tags=["supervisor"])

api_router.include_router(supervisor_complaints.router, prefix="/api/v1")
api_router.include_router(supervisor_reports.router, prefix="/api/v1")
api_router.include_router(supervisor_mess_menu.router, prefix="/api/v1")
api_router.include_router(supervisor_announcement.router, prefix="/api/v1")
api_router.include_router(supervisor_module_router, prefix="/supervisor", tags=["Supervisor Module"])

#=============================================================

#=============================================================
#student dashboard
api_router.include_router(student_complaints.router, prefix="/api/v1")
api_router.include_router(student_mess_menu.router, prefix="/api/v1")
api_router.include_router(student_announcement.router, prefix="/api/v1")
 
#=============================================================

#=============================================================
#visitor dasboard
api_router.include_router(visitor_search.router, prefix="/api/v1")
#=============================================================


















