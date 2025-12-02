# # app/api/v1/routers/templates.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import SessionLocal,get_db
# from app.models.payment_models import ReminderTemplate, ReminderType
# from app.schemas.payment_schemas import TemplateCreate, TemplateResponse

# router = APIRouter(prefix="/reminders/templates", tags=["Reminder Templates"])


# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()


# # -----------------------------------------------------------
# # Create template
# # -----------------------------------------------------------

# @router.post("/", response_model=TemplateResponse)
# def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
#     new_template = ReminderTemplate(**template.dict())
#     db.add(new_template)
#     db.commit()
#     db.refresh(new_template)
#     return new_template


# # -----------------------------------------------------------
# # Get templates
# # -----------------------------------------------------------

# @router.get("/", response_model=list[TemplateResponse])
# def get_templates(reminder_type: ReminderType = None, db: Session = Depends(get_db)):

#     query = db.query(ReminderTemplate)
#     if reminder_type:
#         query = query.filter(ReminderTemplate.reminder_type == reminder_type)

#     return query.all()
# app/api/v1/routers/templates.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.payment_models import ReminderTemplate, ReminderType
from app.schemas.payment_schemas import TemplateCreate, TemplateResponse

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

router = APIRouter(prefix="/reminders/templates", tags=["Reminder Templates"])


# -----------------------------------------------------------
# Create template
# Roles: Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/", response_model=TemplateResponse)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_REMINDERS)),
):
    new_template = ReminderTemplate(**template.dict())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


# -----------------------------------------------------------
# Get templates
# Roles: Admin + SuperAdmin + Supervisor
# -----------------------------------------------------------
@router.get("/", response_model=list[TemplateResponse])
def get_templates(
    reminder_type: ReminderType = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_REMINDERS)),
):
    query = db.query(ReminderTemplate)

    if reminder_type:
        query = query.filter(ReminderTemplate.reminder_type == reminder_type)

    return query.all()
