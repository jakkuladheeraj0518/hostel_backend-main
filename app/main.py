"""
FastAPI main application entry point.
Combines: CORS, Routers, Middleware, DB Init, Elasticsearch Init, OpenAPI overrides.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles


from app.config import settings
from app.core.logger import setup_logger
from app.core.database import init_db
from app.core.elasticsearch import init_elasticsearch_indices

from app.services.booking_expiry_service import BookingExpiryService
from app.core.database import SessionLocal

# Middleware
from app.middleware.authentication import AuthenticationMiddleware
from app.middleware.tenant_filter import TenantFilterMiddleware
from app.middleware.role_enforcer import RoleEnforcerMiddleware
from app.middleware.audit_trail import AuditTrailMiddleware


# ---------------------------------------------------------
# ⭐ NOTIFICATION ROUTERS
# ---------------------------------------------------------
from app.api.v1.student.notification import router as student_notification_router
from app.api.v1.supervisor.notification import router as supervisor_notification_router
from app.api.v1.admin.notification import router as admin_notification_router
from app.api.v1.webhooks.notifications import router as notification_webhook_router
# ---------------------------------------------------------


# Routers (core / existing)
from app.api.v1.router import api_router
from app.api.v1.student import complaints as student_complaints
from app.api.v1.supervisor import complaints as supervisor_complaints
from app.api.v1.admin import complaints as admin_complaints
from app.api.v1.visitor import search as visitor_search
from app.api.v1.super_admin import (
    hostels, dashboard, admins, subscription,
    analytics, reports, shift_coordination
)
from app.api.v1.super_admin import report as super_admin_reports
from app.api.v1.admin import reports as admin_reports
from app.api.v1.supervisor import reports as supervisor_reports

# Admin model-wise routers
from app.api.v1.admin.rooms import router as rooms_router
from app.api.v1.admin.beds import router as beds_router
from app.api.v1.admin.students import router as students_router
from app.api.v1.admin.supervisors import router as supervisors_router
from app.api.v1.admin.comparison_router import router as comparison_router
from app.api.v1.admin import (
    fee_structure_configuration,
    payment_routers as payment_routes,
    transactions,
)

# ⭐ Mess Menu & Announcement Imports
from app.api.v1.admin import mess_menu as admin_mess_menu
from app.api.v1.supervisor import mess_menu as supervisor_mess_menu
from app.api.v1.student import mess_menu as student_mess_menu

from app.api.v1.admin import announcement as admin_announcement
from app.api.v1.supervisor import announcement as supervisor_announcement
from app.api.v1.student import announcement as student_announcement

# Visitor Routers
from app.api.v1.visitor.bookings import router as visitor_booking_router
from app.api.v1.visitor.public_comparison import router as visitor_compare_router

# ⭐ MISSING FROM YOUR OFFICIAL MAIN — NOW ADDED
from app.api.v1.visitor import auth_router, booking_router, payment_routers, simple_payment_router

# Admin Routers
from app.api.v1.admin.bookings import router as admin_booking_router
from app.api.v1.admin.bookings_modify import router as admin_modify_booking_router

# NEW: Calendar Router
from app.api.v1.admin.calendar import router as calendar_router

# NEW: Waitlist Routers (admin + visitor)
from app.api.v1.admin.waitlist import router as admin_waitlist_router
from app.api.v1.visitor.waitlist import router as visitor_waitlist_router

# NEW: Admin Scheduled Jobs
from app.api.v1.admin.admin_jobs import router as admin_jobs_router

# Logger
logger = setup_logger()

# ---------------------------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Hostel Management System API",
    description="Comprehensive hostel management system with JWT Auth, RBAC, Complaints, Analytics, Search",
    version="1.0.0",
    debug=settings.DEBUG
)

# ---------------------------------------------------------------------------
# CORS CONFIG
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# MIDDLEWARE PIPELINE
# ---------------------------------------------------------------------------
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(TenantFilterMiddleware)
app.add_middleware(RoleEnforcerMiddleware)
app.add_middleware(AuditTrailMiddleware)

# ---------------------------------------------------------------------------
# CUSTOM OPENAPI
# ---------------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Hostel Management System API",
        version="1.0.0",
        description="Comprehensive hostel management system with JWT Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    public_routes = ["/", "/health", "/api/v1/auth/login"]
    for path, item in openapi_schema["paths"].items():
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            continue
        if path in public_routes:
            continue
        for method in item:
            if "security" not in item[method]:
                item[method]["security"] = [{"HTTPBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ---------------------------------------------------------------------------
# STARTUP EVENTS
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")

    logger.info("Initializing Elasticsearch...")
    init_elasticsearch_indices()
    logger.info("Elasticsearch ready.")

    # ⭐ Start expiry service
    expiry = BookingExpiryService(SessionLocal)
    expiry.start()

    # ⭐ Start Notification Worker
    logger.info("Notification worker started.")

# ---------------------------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------------------------

# Core routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api/v1")
app.include_router(student_complaints.router, prefix="/api/v1")
app.include_router(supervisor_complaints.router, prefix="/api/v1")
app.include_router(supervisor_reports.router, prefix="/api/v1")
app.include_router(admin_complaints.router, prefix="/api/v1")
app.include_router(admin_reports.router, prefix="/api/v1")
app.include_router(super_admin_reports.router, prefix="/api/v1")
app.include_router(visitor_search.router, prefix="/api/v1")

# ⭐ Added Visitor Authentication/Booking/Payment Routers
app.include_router(booking_router.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(payment_routers.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(simple_payment_router.router, prefix="/api/v1/simple-payments", tags=["SimplePayments"])

# Super-admin
app.include_router(hostels.router)
app.include_router(dashboard.router)
app.include_router(admins.router)
app.include_router(subscription.router)
app.include_router(reports.router)
app.include_router(analytics.router)
app.include_router(shift_coordination.router)

# Admin model-wise
app.include_router(rooms_router)
app.include_router(beds_router)
app.include_router(students_router)
app.include_router(supervisors_router)

# Comparison
app.include_router(comparison_router)

# Additional routers
app.include_router(visitor_booking_router)
app.include_router(visitor_compare_router)
app.include_router(admin_booking_router)
app.include_router(admin_modify_booking_router)
app.include_router(calendar_router)
app.include_router(admin_waitlist_router)
app.include_router(visitor_waitlist_router)
app.include_router(admin_jobs_router)

# Fee & Payment
app.include_router(fee_structure_configuration.router)
app.include_router(payment_routes.router)

from app.api.v1.admin import invoices, transactions, receipts, refunds
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
app.include_router(refunds.router, prefix="/refunds", tags=["Refunds"])

from app.api.v1.admin.ledger_routes import router as ledger_router
app.include_router(ledger_router)

from app.api.v1.admin.reminder_configs import router as reminder_config_router
app.include_router(reminder_config_router)

from app.api.v1.admin.reminder_templates import router as reminder_template_router
app.include_router(reminder_template_router)

from app.api.v1.admin.Reminder_rotes import router as reminder_router
app.include_router(reminder_router)

# ⭐ Mess Menu Routers
app.include_router(admin_mess_menu.router, prefix="/api/v1")
app.include_router(supervisor_mess_menu.router, prefix="/api/v1")
app.include_router(student_mess_menu.router, prefix="/api/v1")

# ⭐ Announcement Routers
app.include_router(admin_announcement.router, prefix="/api/v1")
app.include_router(supervisor_announcement.router, prefix="/api/v1")
app.include_router(student_announcement.router, prefix="/api/v1")

# ---------------------------------------------------------
# ⭐ NOTIFICATION ROUTERS (FINAL STEP)
# ---------------------------------------------------------
app.include_router(
    student_notification_router,
    prefix="/api/v1/student/notifications",
    tags=["Student Notifications"]
)

app.include_router(
    supervisor_notification_router,
    prefix="/api/v1/supervisor/notifications",
    tags=["Supervisor Notifications"]
)

app.include_router(
    admin_notification_router,
    prefix="/api/v1/admin/notifications",
    tags=["Admin Notifications"]
)

# Webhook for delivery tracking (SendGrid / Twilio)
app.include_router(
    notification_webhook_router,
    prefix="/api/v1/webhooks/notifications",
    tags=["Notification Webhooks"]
)

# ---------------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------------
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ---------------------------------------------------------------------------
# HEALTH & ROOT
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Hostel Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", operation_id="health_check_status")
async def health_check():
    return {"status": "healthy"}

# ---------------------------------------------------------------------------
# RUN LOCALLY
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
