"""
Supervisor Module
Provides endpoints for hostel supervisors to manage complaints, attendance, and leave applications.
"""

from app.api.v1.supervisor.routes import router

__all__ = ["router"]
