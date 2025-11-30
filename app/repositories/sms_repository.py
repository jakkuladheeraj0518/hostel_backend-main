from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.models.sms_models import (
    SMSTemplate, SMSLog, OTP, PaymentReminder, EmergencyAlert,
    OTPStatus, SMSStatus
)


# ============================================================
# TEMPLATE REPOSITORY
# ============================================================

class TemplateRepository:

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[SMSTemplate]:
        return db.query(SMSTemplate).filter(
            SMSTemplate.name == name,
            SMSTemplate.is_active == True
        ).first()

    @staticmethod
    def create(db: Session, data: dict) -> SMSTemplate:
        obj = SMSTemplate(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def list(db: Session, message_type=None, skip=0, limit=100) -> List[SMSTemplate]:
        q = db.query(SMSTemplate).filter(SMSTemplate.is_active == True)
        if message_type:
            q = q.filter(SMSTemplate.message_type == message_type)
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def deactivate(db: Session, template_id: int) -> bool:
        template = db.query(SMSTemplate).filter(SMSTemplate.id == template_id).first()
        if not template:
            return False
        template.is_active = False
        db.commit()
        return True


# ============================================================
# SMS LOG REPOSITORY
# ============================================================

class SMSLogRepository:

    @staticmethod
    def create(db: Session, data: dict) -> SMSLog:
        log = SMSLog(**data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update(db: Session, log: SMSLog, updates: dict) -> SMSLog:
        for k, v in updates.items():
            setattr(log, k, v)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_logs(
        db: Session,
        phone_number: Optional[str] = None,
        status: Optional[SMSStatus] = None,
        message_type=None
    ) -> List[SMSLog]:

        q = db.query(SMSLog)

        if phone_number:
            q = q.filter(SMSLog.phone_number == phone_number)
        if status:
            q = q.filter(SMSLog.status == status)
        if message_type:
            q = q.filter(SMSLog.message_type == message_type)

        return q.order_by(SMSLog.created_at.desc()).all()


# ============================================================
# OTP REPOSITORY
# ============================================================

class OTPRepository:

    @staticmethod
    def get_active(db: Session, phone: str, purpose: str) -> Optional[OTP]:
        return db.query(OTP).filter(
            OTP.phone_number == phone,
            OTP.purpose == purpose,
            OTP.status == OTPStatus.active,
            OTP.expires_at > datetime.utcnow()
        ).first()

    @staticmethod
    def create(db: Session, data: dict) -> OTP:
        otp = OTP(**data)
        db.add(otp)
        db.commit()
        db.refresh(otp)
        return otp

    @staticmethod
    def set_verified(db: Session, otp: OTP):
        otp.status = OTPStatus.verified
        otp.verified_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def set_expired(db: Session, otp: OTP):
        otp.status = OTPStatus.expired
        db.commit()

    @staticmethod
    def increment_attempts(db: Session, otp: OTP):
        otp.attempts += 1
        db.commit()

    @staticmethod
    def mark_failed(db: Session, otp: OTP):
        otp.status = OTPStatus.failed
        db.commit()

    @staticmethod
    def link_sms_log(db: Session, otp: OTP, log_id: int):
        otp.sms_log_id = log_id
        db.commit()


# ============================================================
# PAYMENT REMINDER REPOSITORY
# ============================================================

class PaymentReminderRepository:

    @staticmethod
    def create(db: Session, data: dict) -> PaymentReminder:
        obj = PaymentReminder(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, reminder_id: int) -> Optional[PaymentReminder]:
        return db.query(PaymentReminder).filter(PaymentReminder.id == reminder_id).first()

    @staticmethod
    def list(db: Session, sent: Optional[bool] = None) -> List[PaymentReminder]:
        q = db.query(PaymentReminder)
        if sent is not None:
            q = q.filter(PaymentReminder.reminder_sent == sent)
        return q.all()

    @staticmethod
    def mark_sent(db: Session, reminder: PaymentReminder, log_id: int):
        reminder.reminder_sent = True
        reminder.sms_log_id = log_id
        reminder.sent_at = datetime.utcnow()
        db.commit()


# ============================================================
# EMERGENCY ALERT REPOSITORY
# ============================================================

class EmergencyAlertRepository:

    @staticmethod
    def create(db: Session, data: dict) -> EmergencyAlert:
        obj = EmergencyAlert(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update_counts(db: Session, alert: EmergencyAlert, sent: int, failed: int):
        alert.sent_count = sent
        alert.failed_count = failed
        alert.sent_at = datetime.utcnow()
        db.commit()
