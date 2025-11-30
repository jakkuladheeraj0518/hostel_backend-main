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

router = APIRouter(prefix="/email", tags=["Email"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Template CRUD
@router.post("/templates", response_model=EmailTemplateResponse)
def create_template(data: EmailTemplateCreate, db: Session = Depends(get_db)):
    return EmailTemplateRepository.create(db, data.dict())

@router.get("/templates", response_model=List[EmailTemplateResponse])
def list_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmailTemplateRepository.list(db, skip=skip, limit=limit)

@router.get("/templates/{id}", response_model=EmailTemplateResponse)
def get_template(id: int, db: Session = Depends(get_db)):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return obj

@router.put("/templates/{id}", response_model=EmailTemplateResponse)
def update_template(id: int, data: EmailTemplateCreate, db: Session = Depends(get_db)):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplateRepository.update(db, obj, data.dict())

@router.delete("/templates/{id}")
def delete_template(id: int, db: Session = Depends(get_db)):
    obj = EmailTemplateRepository.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    EmailTemplateRepository.deactivate(db, obj)
    return {"message": "Template disabled"}

# Send Email
@router.post("/send", response_model=EmailLogResponse)
def send_email(request: SendEmailRequest, db: Session = Depends(get_db)):
    return EmailService.send_email(db, request)

# Logs
@router.get("/logs", response_model=List[EmailLogResponse])
def list_logs(skip: int = 0, limit: int = 100, recipient: Optional[str] = None,
              status: Optional[EmailStatus] = None, db: Session = Depends(get_db)):
    return EmailLogRepository.list_logs(db, recipient=recipient, status=status, skip=skip, limit=limit)

@router.get("/logs/{id}", response_model=EmailLogResponse)
def get_log(id: int, db: Session = Depends(get_db)):
    log = EmailLogRepository.get_log(db, id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
