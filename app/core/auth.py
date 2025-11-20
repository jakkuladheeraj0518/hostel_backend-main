"""
Authentication decorators and dependencies
"""
from fastapi import Depends, HTTPException, status, Request
from app.core.security import decode_token
from app.core.roles import Role, get_role_level


async def get_current_user(request: Request):
    """Extract current user from request state"""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return {"user_id": user_id}


async def admin_required(request: Request):
    """Dependency: Require admin role or higher"""
    user_role = getattr(request.state, 'user_role', None)
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    admin_level = get_role_level(Role.ADMIN)
    user_level = get_role_level(user_role)
    
    if user_level < admin_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {"user_role": user_role}


async def visitor_required(request: Request):
    """Dependency: Require visitor role or any authenticated user"""
    user_role = getattr(request.state, 'user_role', None)
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {"user_role": user_role}


async def superadmin_required(request: Request):
    """Dependency: Require superadmin role"""
    user_role = getattr(request.state, 'user_role', None)
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if user_role != Role.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    
    return {"user_role": user_role}


async def supervisor_required(request: Request):
    """Dependency: Require supervisor role or higher"""
    user_role = getattr(request.state, 'user_role', None)
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    supervisor_level = get_role_level(Role.SUPERVISOR)
    user_level = get_role_level(user_role)
    
    if user_level < supervisor_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required"
        )
    
    return {"user_role": user_role}
