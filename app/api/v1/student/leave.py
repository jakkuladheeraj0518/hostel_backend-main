from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import current_user
from app.core.rbac import Role
# Add your imports here

router = APIRouter(prefix="/leave", tags=["Student Leave"])

# Move leave request endpoints here from routes.py
