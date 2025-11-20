"""
🏠 Multi-hostel filtering middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.roles import Role


class TenantMiddleware(BaseHTTPMiddleware):
    """Filter data by hostel_id for multi-tenant support"""
    
    async def dispatch(self, request: Request, call_next):
        # Superadmin can access all hostels
        if hasattr(request.state, "user_role") and request.state.user_role == Role.SUPERADMIN:
            return await call_next(request)
        
        # Extract hostel_id from request state or query params
        if hasattr(request.state, "hostel_id") and request.state.hostel_id:
            request.state.active_hostel_id = request.state.hostel_id
        else:
            # Try to get from query params for session switching
            hostel_id = request.query_params.get("hostel_id")
            if hostel_id:
                request.state.active_hostel_id = int(hostel_id)
        
        return await call_next(request)

