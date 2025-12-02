# from fastapi import APIRouter, Depends, HTTPException
# from typing import List, Optional
# from sqlalchemy.orm import Session
# from app.config import SessionLocal
# from app.schemas.noti_schemas import (
#     EmailTemplateCreate, EmailTemplateResponse,
#     SendEmailRequest, EmailLogResponse
# )
# from app.repositories.noti_repository import EmailTemplateRepository, EmailLogRepository
# from app.services.noti_services import EmailService
# from app.models.noti_models import EmailStatus

# router = APIRouter(prefix="/email", tags=["Email"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Template CRUD
# @router.post("/templates", response_model=EmailTemplateResponse)
# def create_template(data: EmailTemplateCreate, db: Session = Depends(get_db)):
#     return EmailTemplateRepository.create(db, data.dict())


# @router.get("/templates/{id}", response_model=EmailTemplateResponse)
# def get_template(id: int, db: Session = Depends(get_db)):
#     obj = EmailTemplateRepository.get(db, id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Template not found")
#     return obj

# @router.put("/templates/{id}", response_model=EmailTemplateResponse)
# def update_template(id: int, data: EmailTemplateCreate, db: Session = Depends(get_db)):
#     obj = EmailTemplateRepository.get(db, id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Template not found")
#     return EmailTemplateRepository.update(db, obj, data.dict())

# @router.delete("/templates/{id}")
# def delete_template(id: int, db: Session = Depends(get_db)):
#     obj = EmailTemplateRepository.get(db, id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Template not found")
#     EmailTemplateRepository.deactivate(db, obj)
#     return {"message": "Template disabled"}

# # Send Email
# @router.post("/send", response_model=EmailLogResponse)
# def send_email(request: SendEmailRequest, db: Session = Depends(get_db)):
#     return EmailService.send_email(db, request)

# # Logs
# @router.get("/logs", response_model=List[EmailLogResponse])
# def list_logs(skip: int = 0, limit: int = 100, recipient: Optional[str] = None,
#               status: Optional[EmailStatus] = None, db: Session = Depends(get_db)):
#     return EmailLogRepository.list_logs(db, recipient=recipient, status=status, skip=skip, limit=limit)

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from app.config import SessionLocal
from app.schemas.noti_schemas import (
    EmailTemplateCreate, EmailTemplateResponse,
    SendEmailRequest, EmailLogResponse
)
from app.repositories.noti_repository import EmailTemplateRepository, EmailLogRepository
from app.services.noti_services import EmailService
from app.models.noti_models import EmailStatus

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

router = APIRouter(prefix="/email", tags=["Email"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# CREATE TEMPLATE - Admin + SuperAdmin
# ---------------------------------------------------------
@router.post("/templates", response_model=EmailTemplateResponse)
def create_template(
    data: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_EMAIL)),
):
    return EmailTemplateRepository.create(db, data.dict())


# ---------------------------------------------------------
# GET TEMPLATE - Admin + SuperAdmin + Supervisor
# ---------------------------------------------------------
@router.get("/templates/{id}", response_model=EmailTemplateResponse)
def get_template(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_EMAIL)),
):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return obj


# ---------------------------------------------------------
# UPDATE TEMPLATE - Admin + SuperAdmin
# ---------------------------------------------------------
@router.put("/templates/{id}", response_model=EmailTemplateResponse)
def update_template(
    id: int,
    data: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_EMAIL)),
):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplateRepository.update(db, obj, data.dict())


# ---------------------------------------------------------
# DELETE TEMPLATE - Admin + SuperAdmin
# ---------------------------------------------------------
@router.delete("/templates/{id}")
def delete_template(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_EMAIL)),
):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    
    EmailTemplateRepository.deactivate(db, obj)
    return {"message": "Template disabled"}


# ---------------------------------------------------------
# SEND EMAIL - Admin + SuperAdmin + Supervisor
# ---------------------------------------------------------
@router.post("/send", response_model=EmailLogResponse)
def send_email(
    request: SendEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_EMAIL)),
):
    return EmailService.send_email(db, request)


# ---------------------------------------------------------
# LIST EMAIL LOGS - Admin + SuperAdmin + Supervisor
# ---------------------------------------------------------
@router.get("/logs", response_model=List[EmailLogResponse])
def list_logs(
    skip: int = 0, 
    limit: int = 100,
    recipient: Optional[str] = None,
    status: Optional[EmailStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_EMAIL)),
):
    return EmailLogRepository.list_logs(
        db,
        recipient=recipient,
        status=status,
        skip=skip,
        limit=limit
    )
