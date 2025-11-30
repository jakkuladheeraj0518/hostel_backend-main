import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from app.models.api_models import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    FallbackStrategy,
)
from app.models.api_models import NotificationTemplate, UnifiedNotificationLog
from app.utils.api_utils import render_template

EMAIL_SERVICE_URL = "http://localhost:8001"
SMS_SERVICE_URL = "http://localhost:8002"
PUSH_SERVICE_URL = "http://localhost:8003"
ROUTING_ENGINE_URL = "http://localhost:8004"


# ============================================================
# CHANNEL SERVICE HELPERS
# ============================================================

async def send_email(recipient_email: str, subject: str, body: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{EMAIL_SERVICE_URL}/send/", json={
                "recipient": recipient_email,
                "subject": subject,
                "html_content": body
            })
            if resp.status_code == 200:
                return {"success": True, "status": "sent"}
            return {"success": False, "status": "failed"}
    except:
        return {"success": False, "status": "failed"}


async def send_sms(phone: str, message: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{SMS_SERVICE_URL}/send/", json={
                "phone_number": phone,
                "message": message
            })
            if resp.status_code == 200:
                return {"success": True, "status": "sent"}
            return {"success": False, "status": "failed"}
    except:
        return {"success": False, "status": "failed"}


async def send_push(user_id: int, title: str, body: str, data: Dict):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{PUSH_SERVICE_URL}/send/", json={
                "user_ids": [user_id],
                "title": title,
                "body": body,
                "data": data
            })
            if resp.status_code == 200:
                return {"success": True, "status": "sent"}
            return {"success": False, "status": "failed"}
    except:
        return {"success": False, "status": "failed"}


async def route_notification(payload: Dict):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{ROUTING_ENGINE_URL}/notifications/", json=payload)
            if resp.status_code == 200:
                return {"success": True}
    except:
        pass
    return {"success": False}


# ============================================================
# MAIN ORCHESTRATION FUNCTION
# ============================================================

async def process_notification(
    db: Session,
    user_id: int,
    user_role: str,
    hostel_id: Optional[int],
    email: Optional[str],
    phone: Optional[str],
    category,
    priority: NotificationPriority,
    title: str,
    message: str,
    data: Dict,
    channels: List[str],
    template: Optional[NotificationTemplate],
    source_module: Optional[str],
    source_reference_id: Optional[int],
    use_routing: bool
):
    """Unified notification processor."""

    log = UnifiedNotificationLog(
        user_id=user_id,
        user_role=user_role,
        hostel_id=hostel_id,
        recipient_email=email,
        recipient_phone=phone,
        category=category,
        priority=priority,
        title=title,
        message=message,
        data=data,
        channels_attempted=channels,
        source_module=source_module,
        source_reference_id=source_reference_id,
        status=NotificationStatus.pending,
        template_id=template.id if template else None
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Routing Engine
    if use_routing and template and template.requires_routing:
        await route_notification({
            "title": title,
            "message": message,
            "category": category.value,
            "priority": priority.value
        })

    results = {}

    # ======================
    # EMAIL
    # ======================
    if "email" in channels and email:
        content = template.email_template if template else message
        subject = template.email_subject if template else title
        results["email"] = await send_email(email, subject, content)
        log.email_status = results["email"]["status"]

    # ======================
    # SMS
    # ======================
    if "sms" in channels and phone:
        sms_body = template.sms_template if template else message
        results["sms"] = await send_sms(phone, sms_body)
        log.sms_status = results["sms"]["status"]

    # ======================
    # PUSH
    # ======================
    if "push" in channels:
        push_title = template.push_title if template else title
        push_body = template.push_body if template else message
        results["push"] = await send_push(user_id, push_title, push_body, data)
        log.push_status = results["push"]["status"]

    # ======================
    # Status decision
    # ======================
    success = [r for r in results.values() if r["success"]]
    total = len(results)

    if len(success) == 0:
        log.status = NotificationStatus.failed
    elif len(success) < total:
        log.status = NotificationStatus.partially_sent
    else:
        log.status = NotificationStatus.sent

    log.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(log)

    return log
