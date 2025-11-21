"""
Supervisor API module
Combines all supervisor-related endpoints
"""
from fastapi import APIRouter

from app.api.v1.supervisor import (
    dashboard,
    attendance,
    leave_management,
    complaints,
    students
)

# Create main supervisor router
supervisor_router = APIRouter(prefix="/supervisor", tags=["Supervisor"])

# Include all sub-routers
supervisor_router.include_router(dashboard.router)
supervisor_router.include_router(attendance.router)
supervisor_router.include_router(leave_management.router)
supervisor_router.include_router(complaints.router)
supervisor_router.include_router(students.router)

__all__ = ["supervisor_router"]
