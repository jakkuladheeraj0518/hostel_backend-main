from sqlalchemy.orm import Session
from app.models.noti_models import EmailTemplate, EmailLog

class EmailTemplateRepository:

    @staticmethod
    def create(db: Session, data: dict):
        obj = EmailTemplate(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        return db.query(EmailTemplate).filter(EmailTemplate.is_active == True).offset(skip).limit(limit).all()

    @staticmethod
    def get(db: Session, id: int):
        return db.query(EmailTemplate).filter(EmailTemplate.id == id).first()

    @staticmethod
    def update(db: Session, obj: EmailTemplate, data: dict):
        for k, v in data.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def deactivate(db: Session, obj: EmailTemplate):
        obj.is_active = False
        db.commit()


class EmailLogRepository:

    @staticmethod
    def create_log(db: Session, data: dict):
        log = EmailLog(**data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update_log(db: Session, log: EmailLog, data: dict):
        for k, v in data.items():
            setattr(log, k, v)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def list_logs(db: Session, recipient=None, status=None, skip: int = 0, limit: int = 100):
        query = db.query(EmailLog)
        if recipient:
            query = query.filter(EmailLog.recipient == recipient)
        if status:
            query = query.filter(EmailLog.status == status)
        return query.order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_log(db: Session, id: int):
        return db.query(EmailLog).filter(EmailLog.id == id).first()
