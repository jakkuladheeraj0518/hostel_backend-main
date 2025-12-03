

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config import get_db
from app.schemas.api_schemas import (
    NotificationTemplateCreate, NotificationTemplateResponse,
    SendNotificationRequest, BroadcastNotificationRequest,
    UnifiedNotificationResponse, UserChannelPreferenceUpdate,
)
from app.models.api_models import NotificationTemplate, NotificationBatch
from app.services.api_services import process_notification
from app.utils.api_utils import render_template, get_user_channel_preferences
from app.models.api_models import NotificationCategory, UserRole

# RBAC
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

router = APIRouter(prefix="/routing", tags=["Routing & Notifications"])


# ============================================================
# TEMPLATE CRUD
# ============================================================

# -----------------------------
# CREATE TEMPLATE - Admin Only
# -----------------------------
@router.post("/templates/", response_model=NotificationTemplateResponse)
def create_template(
    request: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_REMINDERS)),
):
    template = NotificationTemplate(**request.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


# -----------------------------
# LIST TEMPLATES - Admin + Supervisor
# -----------------------------
@router.get("/templates/", response_model=List[NotificationTemplateResponse])
def list_templates(
    category: Optional[NotificationCategory] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_REMINDERS)),
):
    query = db.query(NotificationTemplate).filter(NotificationTemplate.is_active == True)
    if category:
        query = query.filter(NotificationTemplate.category == category)
    return query.all()


# -----------------------------
# GET SINGLE TEMPLATE - Admin + Supervisor
# -----------------------------
@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_REMINDERS)),
):
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(404, "Template not found")
    return template


# ============================================================
# SEND NOTIFICATION (individual)
# ============================================================
@router.post("/send/", response_model=UnifiedNotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_NOTIFICATIONS)),
):
    template = None
    title = request.title
    message = request.message

    if request.template_name:
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.name == request.template_name
        ).first()
        if not template:
            raise HTTPException(404, "Template not found")

        if template.email_subject:
            title = render_template(template.email_subject, request.variables)
        if template.sms_template:
            message = render_template(template.sms_template, request.variables)

    channels = (
        [ch.value for ch in request.channels]
        if request.channels else template.enabled_channels
        if template else get_user_channel_preferences(db, request.user_id, request.category)
    )

    log = await process_notification(
        db,
        request.user_id,
        request.user_role.value,
        request.hostel_id,
        request.recipient_email,
        request.recipient_phone,
        request.category,
        request.priority,
        title or "Notification",
        message or "",
        request.data,
        channels,
        template,
        request.source_module,
        request.source_reference_id,
        request.use_routing_engine
    )

    return log


# ============================================================
# BROADCAST NOTIFICATION - Admin + SuperAdmin Only
# ============================================================
@router.post("/broadcast/")
async def broadcast_notification(
    request: BroadcastNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_NOTIFICATIONS)),
):
    batch = NotificationBatch(
        batch_name=f"{request.category.value}_batch",
        category=request.category,
        created_by=request.created_by,
        created_by_role=request.created_by_role,
        status="processing"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    users = request.user_ids or []

    for user_id in users:
        channels = (
            [ch.value for ch in request.channels]
            if request.channels else get_user_channel_preferences(db, user_id, request.category)
        )

        await process_notification(
            db,
            user_id,
            request.user_role.value if request.user_role else UserRole.student.value,
            request.hostel_ids[0] if request.hostel_ids else None,
            None, None,
            request.category,
            request.priority,
            request.title,
            request.message,
            request.data,
            channels,
            None,
            request.source_module,
            None,
            False,
        )

    batch.status = "completed"
    db.commit()

    return {"batch_id": batch.id, "sent_to": len(users)}



