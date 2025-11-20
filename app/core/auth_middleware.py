"""
🧠 Auth + Role verification middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token
from app.core.roles import get_role_level


class AuthMiddleware(BaseHTTPMiddleware):
    """Verify JWT token and extract user info"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/", "/health", "/api/v1/auth/login"]:
            return await call_next(request)
        
        # Extract token from header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        try:
            payload = decode_token(token)
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            request.state.hostel_id = payload.get("hostel_id")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return await call_next(request)

