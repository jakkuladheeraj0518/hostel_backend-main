# app/services/reminder_service.py

from datetime import datetime
import uuid
import json
from sqlalchemy.orm import Session
from app.models.payment_models import (
    Invoice, ReminderConfiguration, PaymentReminder, ReminderType,
    ReminderChannel, ReminderStatus, ReminderTemplate
)
from app.utils.email_utilss import send_email_reminder
from app.utils.sms_utilss import send_sms_reminder
from app.utils.template_utilss import render_template


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------

def generate_reminder_id():
    return f"REM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"


def get_template_context(invoice: Invoice):
    """Generate template variables."""
    user = invoice.user
    hostel = invoice.hostel

    now = datetime.utcnow()
    days_overdue = max((now - invoice.due_date).days, 0)

    return {
        "user_name": user.name,
        "invoice_number": invoice.invoice_number,
        "amount": f"₹{invoice.due_amount:.2f}",
        "total_amount": f"₹{invoice.total_amount:.2f}" if hasattr(invoice, "total_amount") else "",
        "paid_amount": f"₹{invoice.paid_amount:.2f}",
        "due_date": invoice.due_date.strftime("%d-%b-%Y"),
        "days_overdue": days_overdue,
        "hostel_name": hostel.name,
        "hostel_phone": hostel.phone or "N/A",
        "hostel_email": hostel.email or "N/A",
        "payment_link": f"https://hostelpay.com/pay/{invoice.invoice_number}"
    }


def get_default_template(reminder_type: ReminderType, db: Session):
    return db.query(ReminderTemplate).filter(
        ReminderTemplate.reminder_type == reminder_type,
        ReminderTemplate.is_default == True
    ).first()


# -----------------------------------------------------------
# Core: Create Reminder
# -----------------------------------------------------------

def create_and_schedule_reminder(invoice: Invoice, reminder_type: ReminderType, channel: ReminderChannel, db: Session):
    user = invoice.user

    template = get_default_template(reminder_type, db)
    if not template:
        print(f"No template found for {reminder_type}")
        return

    context = get_template_context(invoice)

    subject = render_template(template.email_subject, context)
    email_body = render_template(template.email_body, context)
    sms_body = render_template(template.sms_body, context)

    reminder = PaymentReminder(
        reminder_id=generate_reminder_id(),
        invoice_id=invoice.id,
        reminder_type=reminder_type,
        channel=channel,
        recipient_email=user.email,
        recipient_phone=user.phone,
        subject=subject,
        message_body=email_body,
        scheduled_at=datetime.utcnow(),
        status=ReminderStatus.PENDING
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    # Send instantly (real world: background worker)
    process_single_reminder(reminder.id, db)


# -----------------------------------------------------------
# Send Actual Emails/SMS
# -----------------------------------------------------------

def process_single_reminder(reminder_id: int, db: Session):
    reminder = db.query(PaymentReminder).filter(PaymentReminder.id == reminder_id).first()
    if not reminder:
        print("Reminder not found")
        return

    invoice = reminder.invoice
    user = invoice.user

    email_success = False
    sms_success = False

    # EMAIL
    if reminder.channel in [ReminderChannel.EMAIL, ReminderChannel.BOTH]:
        if user.email and user.email_notifications:
            email_success = send_email_reminder(
                reminder.recipient_email,
                reminder.subject,
                reminder.message_body
            )

    # SMS
    if reminder.channel in [ReminderChannel.SMS, ReminderChannel.BOTH]:
        if user.phone and user.sms_notifications:
            sms_success = send_sms_reminder(reminder.recipient_phone, reminder.message_body)

    # Update status
    if email_success or sms_success:
        reminder.status = ReminderStatus.SENT
        reminder.sent_at = datetime.utcnow()
        invoice.last_reminder_sent = datetime.utcnow()
        invoice.reminder_count += 1
    else:
        reminder.status = ReminderStatus.FAILED

    db.commit()


# -----------------------------------------------------------
# Automated Invoice Processing
# -----------------------------------------------------------

def process_invoice_reminders(invoice: Invoice, db: Session):
    now = datetime.utcnow()
    config = db.query(ReminderConfiguration).filter(
        ReminderConfiguration.hostel_id == invoice.hostel_id
    ).first()

    if not config:
        return

    if invoice.reminder_count >= config.max_reminders:
        return

    days_until_due = (invoice.due_date - now).days
    days_overdue = (now - invoice.due_date).days if now > invoice.due_date else 0

    reminder_type = None
    channel = None

    # 1️⃣ Pre-due reminders
    if days_until_due > 0:
        days_list = [int(d.strip()) for d in config.pre_due_days.split(",")]
        if days_until_due in days_list:
            reminder_type = ReminderType.PRE_DUE
            channel = config.pre_due_channels

    # 2️⃣ Due date reminder
    elif days_until_due == 0 and config.due_date_enabled:
        reminder_type = ReminderType.DUE_DATE
        channel = config.due_date_channels

    # 3️⃣ Overdue & Escalation
    elif days_overdue > 0:

        if config.escalation_enabled:

            if days_overdue >= config.final_notice_days and invoice.escalation_level < 4:
                reminder_type = ReminderType.FINAL_NOTICE
                channel = ReminderChannel.BOTH
                invoice.escalation_level = 4

            elif days_overdue >= config.escalation_3_days and invoice.escalation_level < 3:
                reminder_type = ReminderType.ESCALATION_3
                channel = ReminderChannel.BOTH
                invoice.escalation_level = 3

            elif days_overdue >= config.escalation_2_days and invoice.escalation_level < 2:
                reminder_type = ReminderType.ESCALATION_2
                channel = ReminderChannel.BOTH
                invoice.escalation_level = 2

            elif days_overdue >= config.escalation_1_days and invoice.escalation_level < 1:
                reminder_type = ReminderType.ESCALATION_1
                channel = ReminderChannel.BOTH
                invoice.escalation_level = 1

        if not reminder_type:
            if not invoice.last_reminder_sent or \
                (now - invoice.last_reminder_sent).days >= config.overdue_frequency_days:

                reminder_type = ReminderType.OVERDUE
                channel = config.overdue_channels

    # 4️⃣ If reminder needed, create it
    if reminder_type and channel:
        create_and_schedule_reminder(invoice, reminder_type, channel, db)


# -----------------------------------------------------------
# Scheduler Processing Loop
# -----------------------------------------------------------

def process_automated_reminders(db: Session):
    invoices = db.query(Invoice).filter(
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).all()

    for invoice in invoices:
        process_invoice_reminders(invoice, db)

    db.commit()
