from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from app.config import get_db
from app.models.sms_models import (
    SMSTemplate, SMSLog, OTPS, PaymentReminders, EmergencyAlert,
    SMSProvider, SMSStatus, MessageType, OTPStatus
)
from app.schemas.sms_schemas import (
    SMSTemplateCreate, SMSTemplateResponse,
    SendSMSRequest, SMSLogResponse,
    SendOTPRequest, VerifyOTPRequest, OTPResponse,
    PaymentReminderCreate, EmergencyAlertCreate
)
from app.utils.sms_utils import generate_otp, hash_otp, render_template
from app.services.sms_services import TwilioService, AWSSNSService


router = APIRouter(prefix="/sms", tags=["SMS Service"])


# ============================================================
# INTERNAL SENDER FUNCTION
# ============================================================

async def send_sms_internal(
    db: Session,
    phone_number: str,
    message: str,
    provider: SMSProvider,
    message_type: MessageType,
    template_id: Optional[int] = None
):
    log = SMSLog(
        phone_number=phone_number,
        message=message,
        message_type=message_type,
        template_id=template_id,
        provider=provider,
        status=SMSStatus.pending
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        service = TwilioService() if provider == SMSProvider.twilio else AWSSNSService()
        sid, status = service.send_sms(phone_number, message)

        log.status = SMSStatus.sent if status in ("sent", "queued") else SMSStatus.failed
        log.message_sid = sid
        log.sent_at = datetime.utcnow()

    except Exception as e:
        log.status = SMSStatus.failed
        log.error_message = str(e)

    db.commit()
    db.refresh(log)
    return log


# ============================================================
# TEMPLATES CRUD
# ============================================================

@router.post("/templates/", response_model=SMSTemplateResponse)
def create_template(data: SMSTemplateCreate, db: Session = Depends(get_db)):
    obj = SMSTemplate(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/templates/", response_model=List[SMSTemplateResponse])
def list_templates(
    skip: int = 0, limit: int = 100,
    message_type: Optional[MessageType] = None,
    db: Session = Depends(get_db)
):
    q = db.query(SMSTemplate).filter(SMSTemplate.is_active == True)
    if message_type:
        q = q.filter(SMSTemplate.message_type == message_type)
    return q.offset(skip).limit(limit).all()


# @router.get("/templates/{id}", response_model=SMSTemplateResponse)
# def get_template(id: int, db: Session = Depends(get_db)):
#     t = db.query(SMSTemplate).filter(SMSTemplate.id == id).first()
#     if not t:
#         raise HTTPException(404, "Template not found")
#     return t


# @router.put("/templates/{id}", response_model=SMSTemplateResponse)
# def update_template(id: int, data: SMSTemplateCreate, db: Session = Depends(get_db)):
#     t = db.query(SMSTemplate).filter(SMSTemplate.id == id).first()
#     if not t:
#         raise HTTPException(404, "Template not found")

#     for k, v in data.dict().items():
#         setattr(t, k, v)

#     t.updated_at = datetime.utcnow()
#     db.commit()
#     db.refresh(t)
#     return t


@router.delete("/templates/{id}")
def delete_template(id: int, db: Session = Depends(get_db)):
    t = db.query(SMSTemplate).filter(SMSTemplate.id == id).first()
    if not t:
        raise HTTPException(404, "Template not found")

    t.is_active = False
    db.commit()
    return {"message": "Template deactivated"}


# ============================================================
# SEND SMS
# ============================================================

@router.post("/send/", response_model=SMSLogResponse)
async def send_sms(request: SendSMSRequest, db: Session = Depends(get_db)):
    message = request.message
    template_id = None

    if request.template_name:
        t = db.query(SMSTemplate).filter(
            SMSTemplate.name == request.template_name,
            SMSTemplate.is_active == True
        ).first()

        if not t:
            raise HTTPException(404, "Template not found")

        message = render_template(t.content, request.variables)
        template_id = t.id

    if not message:
        raise HTTPException(400, "Message or template_name required")

    return await send_sms_internal(
        db, request.phone_number, message,
        request.provider, request.message_type, template_id
    )


# ============================================================
# OTP MANAGEMENT
# ============================================================

@router.post("/otp/send/", response_model=OTPResponse)
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):

    existing = db.query(OTPS).filter(
        OTPS.phone_number == request.phone_number,
        OTPS.purpose == request.purpose,
        OTPS.status == OTPStatus.active,
        OTPS.expires_at > datetime.utcnow()
    ).first()

    if existing:
        raise HTTPException(400, "Active OTP already exists")

    # Generate
    code = generate_otp(request.otp_length)
    hashed = hash_otp(code)

    otp = OTPS(
        phone_number=request.phone_number,
        otp_code=code,
        otp_hash=hashed,
        purpose=request.purpose,
        status=OTPStatus.active,
        expires_at=datetime.utcnow() + timedelta(minutes=request.validity_minutes)
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)

    msg = (
        f"Your OTP is {code}. "
        f"Valid for {request.validity_minutes} minutes. Do not share it."
    )

    log = await send_sms_internal(
        db, request.phone_number, msg,
        request.provider, MessageType.otp
    )

    otp.sms_log_id = log.id
    db.commit()

    return otp


@router.post("/otp/verify/")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp = db.query(OTPS).filter(
        OTPS.phone_number == request.phone_number,
        OTPS.purpose == request.purpose,
        OTPS.status == OTPStatus.active
    ).order_by(OTPS.created_at.desc()).first()
    if not otp:
        raise HTTPException(404, "No active OTP")

    if otp.expires_at < datetime.utcnow():
        otp.status = OTPStatus.expired
        db.commit()
        raise HTTPException(400, "OTP expired")

    otp.attempts += 1

    if hash_otp(request.otp_code) == otp.otp_hash:
        otp.status = OTPStatus.verified
        otp.verified_at = datetime.utcnow()
        db.commit()
        return {"verified": True}

    if otp.attempts >= otp.max_attempts:
        otp.status = OTPStatus.failed

    db.commit()
    raise HTTPException(400, "Invalid OTP")


# @router.get("/otp/{phone}", response_model=List[OTPResponse])
# def otp_history(phone: str, db: Session = Depends(get_db)):
#     return db.query(OTP).filter(
#         OTP.phone_number == phone
#     ).order_by(OTP.created_at.desc()).all()


# ============================================================
# PAYMENT REMINDERS
# ============================================================

@router.post("/payment-reminders/")
def create_payment_reminder(data: PaymentReminderCreate, db: Session = Depends(get_db)):
    obj = PaymentReminders(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/payment-reminders/{id}/send")
async def send_payment_reminder(id: int, provider: SMSProvider = SMSProvider.twilio, db: Session = Depends(get_db)):
    r = db.query(PaymentReminders).filter(PaymentReminders.id == id).first()
    if not r:
        raise HTTPException(404, "Reminder not found")

    if r.reminder_sent:
        raise HTTPException(400, "Already sent")

    msg = (
        f"Dear {r.customer_name}, payment of ${r.amount:.2f} "
        f"for invoice {r.invoice_number} is due on {r.due_date.date()}."
    )

    log = await send_sms_internal(
        db, r.phone_number, msg,
        provider, MessageType.payment_reminder
    )

    r.reminder_sent = True
    r.sms_log_id = log.id
    r.sent_at = datetime.utcnow()
    db.commit()

    return {"sms_log_id": log.id, "sent": True}


@router.get("/payment-reminders/")
def list_payment_reminders(db: Session = Depends(get_db), sent: Optional[bool] = None):
    q = db.query(PaymentReminders)
    if sent is not None:
        q = q.filter(PaymentReminders.reminder_sent == sent)
    return q.all()


# ============================================================
# EMERGENCY ALERTS
# ============================================================

@router.post("/emergency-alerts/")
async def create_alert(data: EmergencyAlertCreate, db: Session = Depends(get_db)):
    obj = EmergencyAlert(
        title=data.title,
        message=data.message,
        severity=data.severity,
        target_groups=str(data.phone_numbers),
        total_recipients=len(data.phone_numbers),
        created_by=data.created_by
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    sent = 0
    failed = 0

    for phone in data.phone_numbers:
        try:
            log = await send_sms_internal(
                db,
                phone,
                f"[{data.severity.upper()}] {data.title}: {data.message}",
                SMSProvider.twilio,
                MessageType.emergency_alert
            )
            if log.status == SMSStatus.sent:
                sent += 1
            else:
                failed += 1
        except:
            failed += 1

    obj.sent_count = sent
    obj.failed_count = failed
    obj.sent_at = datetime.utcnow()
    db.commit()

    return {"alert_id": obj.id, "sent": sent, "failed": failed}


# @router.get("/emergency-alerts/")
# def list_alerts(db: Session = Depends(get_db)):
#     return db.query(EmergencyAlert).order_by(EmergencyAlert.created_at.desc()).all()


# ============================================================
# SMS LOGS
# ============================================================

@router.get("/logs/", response_model=List[SMSLogResponse])
def get_sms_logs(
    db: Session = Depends(get_db),
    phone_number: Optional[str] = None,
    status: Optional[SMSStatus] = None,
    message_type: Optional[MessageType] = None,
):
    q = db.query(SMSLog)

    if phone_number:
        q = q.filter(SMSLog.phone_number == phone_number)
    if status:
        q = q.filter(SMSLog.status == status)
    if message_type:
        q = q.filter(SMSLog.message_type == message_type)

    return q.order_by(SMSLog.created_at.desc()).all()


# @router.get("/logs/{id}", response_model=SMSLogResponse)
# def get_log(id: int, db: Session = Depends(get_db)):
#     l = db.query(SMSLog).filter(SMSLog.id == id).first()
#     if not l:
#         raise HTTPException(404, "Log not found")
#     return l


# @router.put("/logs/{id}/status")
# def update_status(id: int, status: SMSStatus, db: Session = Depends(get_db)):
#     l = db.query(SMSLog).filter(SMSLog.id == id).first()
#     if not l:
#         raise HTTPException(404, "Log not found")

#     l.status = status
#     if status == SMSStatus.delivered:
#         l.delivered_at = datetime.utcnow()

#     db.commit()
#     return {"message": "Status updated"}


# ============================================================
# STATISTICS
# ============================================================

@router.get("/stats/")
def stats(db: Session = Depends(get_db)):
    total_sms = db.query(SMSLog).count()
    sent_sms = db.query(SMSLog).filter(SMSLog.status == SMSStatus.sent).count()
    failed_sms = db.query(SMSLog).filter(SMSLog.status == SMSStatus.failed).count()

    total_otp = db.query(OTPS).count()
    verified = db.query(OTPS).filter(OTPS.status == OTPStatus.verified).count()

    return {
        "total_sms": total_sms,
        "successful_sms": sent_sms,
        "failed_sms": failed_sms,
        "total_otps": total_otp,
        "verified_otps": verified,
        "otp_verification_rate":
            f"{(verified/total_otp * 100):.2f}%" if total_otp > 0 else "0%"
    }
