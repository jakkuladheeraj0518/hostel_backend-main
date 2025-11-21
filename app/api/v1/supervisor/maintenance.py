from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import current_user
from app.core.rbac import Role
# Add your imports here

router = APIRouter(prefix="/maintenance", tags=["Supervisor Maintenance"])

# Move maintenance request endpoints here from routes.py
