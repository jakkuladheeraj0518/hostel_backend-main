"""
JWT authentication middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Verify JWT token in request headers"""
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/verify-reset-code",
    "/api/v1/auth/reset-password",
    # Social login endpoints removed per admin request
    "/api/v1/auth/password-strength",
    ]
    
    def is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require auth)"""
        # Exact match
        if path in self.PUBLIC_PATHS:
            return True
        # Check if path starts with any public path
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if self.is_public_path(request.url.path):
            return await call_next(request)
        
        # Extract token
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.split(" ")[1]
        try:
            payload = decode_token(token)
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            request.state.hostel_id = payload.get("hostel_id")
            request.state.email = payload.get("email")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)

