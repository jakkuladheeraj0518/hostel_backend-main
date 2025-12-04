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




# ---------------------------------------------------------
#  NOTIFICATION ROUTERS
# ---------------------------------------------------------
from app.api.v1.admin.api_router import router as admin_notification_router
from app.api.v1.admin.push_router import router as supervisor_notification_router
from app.api.v1.admin.routers import router as student_notification_router
from app.api.v1.admin.routing_router import router as notification_webhook_router
from app.api.v1.admin.sms_router import router as admin_sms_router

from app.api.v1.router import api_router
from app.api.v1.supervisor import router as supervisor_module_router
from app.api.v1.supervisor.auth import router as supervisor_auth_router

# Visitor Routers
from app.api.v1.visitor.bookings import router as visitor_booking_router
from app.api.v1.visitor.public_comparison import router as visitor_compare_router

#  MISSING FROM YOUR OFFICIAL MAIN — NOW ADDED
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
#  Hemant Integration - New Routes
from app.api.v1.student import reviews as student_reviews
from app.api.v1.student import leave_enhanced as student_leave_enhanced
# Removed: admin_review_management (duplicate of admin_reviews)

#  Maintenance & Leave Management Routes
from app.api.v1.admin.preventive_maintenance import router as preventive_maintenance_router
from app.api.v1.admin.maintenance_costs import router as maintenance_costs_router
from app.api.v1.admin.maintenance import router as maintenance_router
from app.api.v1.admin.maintenance_tasks import router as maintenance_tasks_router
from app.api.v1.admin.maintenance_approvals import router as maintenance_approvals_router
from app.api.v1.admin.leave import router as admin_leave_router
from app.api.v1.admin import reviews as admin_reviews
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

# after app = FastAPI(...)
from app.middleware.authentication import authentication_middleware
from app.middleware.tenant_filter import tenant_filter_middleware
from app.middleware.role_enforcer import role_enforcer_middleware
from app.middleware.audit_trail import audit_trail_middleware

# register function-style middlewares in order:
app.middleware("http")(authentication_middleware)
app.middleware("http")(tenant_filter_middleware)
app.middleware("http")(role_enforcer_middleware)
app.middleware("http")(audit_trail_middleware)



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

    #  Start expiry service
    expiry = BookingExpiryService(SessionLocal)
    expiry.start()

    #  Start Notification Worker
    logger.info("Notification worker started.")

# ---------------------------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------------------------

# Core routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api/v1")







#  Added Visitor Authentication/Booking/Payment Routers
app.include_router(booking_router.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(payment_routers.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(simple_payment_router.router, prefix="/api/v1/simple-payments", tags=["SimplePayments"])

# Super-admin



# Additional routers
app.include_router(visitor_booking_router)
app.include_router(visitor_compare_router)
app.include_router(admin_booking_router)
app.include_router(admin_modify_booking_router)
app.include_router(calendar_router)
app.include_router(admin_waitlist_router)
app.include_router(visitor_waitlist_router)
app.include_router(admin_jobs_router)



#  NEW: Supervisor Module Routes (Dashboard, Complaints, Attendance, Leave Management)
app.include_router(
    supervisor_auth_router,
    prefix="/api/v1/auth",
    tags=["Supervisor Authentication"]
)
# NOTE: supervisor_module_router is included on `api_router` (mounted under /api/v1)
# to avoid registering the same routes twice and causing duplicate operationIds.

# ---------------------------------------------------------
#  NOTIFICATION ROUTERS (FINAL STEP)
# ---------------------------------------------------------
app.include_router(admin_notification_router)
app.include_router(supervisor_notification_router)
app.include_router(student_notification_router)
app.include_router(notification_webhook_router)
app.include_router(admin_sms_router)

#  Hemant Integration Routes
app.include_router(
    student_reviews.router,
    prefix="/api/v1",
    tags=["Student Reviews"]
)

app.include_router(
    student_leave_enhanced.router,
    prefix="/api/v1",
    tags=["Student Leave Enhanced"]
)

# Removed duplicate: admin_review_management (same as admin_reviews)

#  Maintenance Management Routes (from image requirements)
app.include_router(
    preventive_maintenance_router,
    prefix="/api/v1/admin",
    tags=["Admin Preventive Maintenance"]
)

app.include_router(
    maintenance_costs_router,
    prefix="/api/v1/admin",
    tags=["Admin Maintenance Costs"]
)

#  NEW: Maintenance Request Management
app.include_router(
    maintenance_router,
    prefix="/api/v1/admin",
    tags=["Admin Maintenance"]
)

#  NEW: Maintenance Task Assignment
app.include_router(
    maintenance_tasks_router,
    prefix="/api/v1/admin",
    tags=["Admin Maintenance Tasks"]
)

#  NEW: Maintenance Approval Workflow
app.include_router(
    maintenance_approvals_router,
    prefix="/api/v1/admin",
    tags=["Admin Maintenance Approvals"]
)

app.include_router(
    admin_leave_router,
    prefix="/api/v1/admin/leave",
    tags=["Admin Leave"]
)

app.include_router(
    admin_reviews.router,
    prefix="/api/v1/admin",
    tags=["Admin Reviews"]
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
