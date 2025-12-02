# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from app.config import get_db
# from app.models.push_models import (
#     DeviceToken, NotificationTemplate, NotificationLog,
#     NotificationPreference, NotificationBatch, HierarchicalRouting,
#     NotificationType, NotificationPriority, NotificationStatus,
#     UserRole, TargetAudience
# )
# from app.schemas.push_schemas import *
# from app.utils.push_utils import render_template
# from app.services.push_services import send_fcm_notification


# router = APIRouter(prefix="/notifications", tags=["Push Notifications"])


# # ============================================================
# # DEVICE TOKENS
# # ============================================================

# @router.post("/device-tokens/", response_model=DeviceTokenResponse)
# def register_token(payload: DeviceTokenCreate, db: Session = Depends(get_db)):
#     existing = db.query(DeviceToken).filter(
#         DeviceToken.device_token == payload.device_token
#     ).first()

#     if existing:
#         for field, value in payload.dict().items():
#             setattr(existing, field, value)
#         existing.is_active = True
#         existing.last_used = datetime.utcnow()
#         db.commit()
#         return existing

#     token = DeviceToken(**payload.dict())
#     db.add(token)
#     db.commit()
#     db.refresh(token)
#     return token


# # ============================================================
# # TEMPLATE CRUD
# # ============================================================

# @router.post("/templates/", response_model=NotificationTemplateResponse)
# def create_template(payload: NotificationTemplateCreate, db: Session = Depends(get_db)):
#     template = NotificationTemplate(**payload.dict())
#     db.add(template)
#     db.commit()
#     return template


# @router.get("/templates/", response_model=List[NotificationTemplateResponse])
# def list_templates(
#     notification_type: Optional[NotificationType] = None,
#     db: Session = Depends(get_db)
# ):
#     q = db.query(NotificationTemplate).filter(NotificationTemplate.is_active == True)
#     if notification_type:
#         q = q.filter(NotificationTemplate.notification_type == notification_type)
#     return q.all()


# # @router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
# # def update_template(template_id: int, payload: NotificationTemplateCreate, db: Session = Depends(get_db)):
# #     t = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
# #     if not t:
# #         raise HTTPException(404, "Not found")

# #     for k, v in payload.dict().items():
# #         setattr(t, k, v)

# #     t.updated_at = datetime.utcnow()
# #     db.commit()
# #     return t


# # ============================================================
# # SEND INDIVIDUAL NOTIFICATIONS
# # ============================================================

# @router.post("/send/")
# async def send_notification(
#     req: SendNotificationRequest,
#     db: Session = Depends(get_db)
# ):

#     title, body = req.title, req.body

#     # Template rendering
#     if req.template_name:
#         t = db.query(NotificationTemplate).filter(
#             NotificationTemplate.name == req.template_name
#         ).first()
#         if not t:
#             raise HTTPException(404, "Template not found")

#         title = render_template(t.title_template, req.variables)
#         body = render_template(t.body_template, req.variables)

#     # Determine recipients
#     users = []
#     if req.user_ids:
#         for uid in req.user_ids:
#             users.append({
#                 "user_id": uid,
#                 "user_role": req.user_role or UserRole.student,
#                 "hostel_id": None
#             })

#     elif req.hostel_ids and req.user_role:
#         tokens = db.query(DeviceToken).filter(
#             DeviceToken.hostel_id.in_(req.hostel_ids),
#             DeviceToken.user_role == req.user_role,
#             DeviceToken.is_active == True
#         ).all()

#         for t in tokens:
#             if not any(u["user_id"] == t.user_id for u in users):
#                 users.append({
#                     "user_id": t.user_id,
#                     "user_role": t.user_role,
#                     "hostel_id": t.hostel_id
#                 })

#     if not users:
#         raise HTTPException(400, "No recipients")

#     sent, failed = 0, 0

#     for u in users:
#         log = NotificationLog(
#             user_id=u["user_id"],
#             user_role=u["user_role"],
#             hostel_id=u["hostel_id"],
#             notification_type=req.notification_type,
#             title=title,
#             body=body,
#             priority=req.priority,
#             status=NotificationStatus.pending,
#         )
#         db.add(log)
#         db.commit()
#         db.refresh(log)

#         tokens = db.query(DeviceToken).filter(
#             DeviceToken.user_id == u["user_id"],
#             DeviceToken.is_active == True
#         ).all()

#         if not tokens:
#             log.status = NotificationStatus.failed
#             log.error_message = "No active tokens"
#             db.commit()
#             failed += 1
#             continue

#         success = False

#         for tkn in tokens:
#             msg_id, err = await send_fcm_notification(
#                 tkn.device_token,
#                 title,
#                 body,
#                 req.data,
#                 req.priority
#             )

#             if msg_id:
#                 success = True
#                 log.fcm_message_id = msg_id
#                 log.status = NotificationStatus.sent
#                 log.sent_at = datetime.utcnow()
#             else:
#                 if "not-found" in str(err) or "invalid" in str(err).lower():
#                     tkn.is_active = False

#         if success:
#             sent += 1
#         else:
#             log.status = NotificationStatus.failed
#             failed += 1

#         db.commit()

#     return {
#         "total": len(users),
#         "sent": sent,
#         "failed": failed
#     }


# # ============================================================
# # BROADCAST NOTIFICATIONS
# # ============================================================

# @router.post("/broadcast/")
# async def broadcast(req: BroadcastNotificationRequest, db: Session = Depends(get_db)):

#     batch = NotificationBatch(
#         batch_name=f"{req.notification_type.value}_{datetime.utcnow().timestamp()}",
#         notification_type=req.notification_type,
#         target_audience=req.target_audience,
#         hostel_ids=req.hostel_ids,
#         room_numbers=req.room_numbers,
#         floor_numbers=req.floor_numbers,
#         user_ids=req.user_ids,
#         created_by=req.created_by,
#         created_by_role=req.created_by_role
#     )
#     db.add(batch)
#     db.commit()
#     db.refresh(batch)

#     q = db.query(DeviceToken).filter(DeviceToken.is_active == True)

#     if req.target_audience == TargetAudience.specific_hostel:
#         q = q.filter(DeviceToken.hostel_id.in_(req.hostel_ids))

#     if req.target_audience == TargetAudience.specific_users and req.user_ids:
#         q = q.filter(DeviceToken.user_id.in_(req.user_ids))

#     if req.target_audience == TargetAudience.all_students:
#         q = q.filter(DeviceToken.user_role == UserRole.student)
#     users = {}
#     for t in q.all():
#         users[f"{t.user_id}_{t.user_role.value}"] = {
#             "user_id": t.user_id,
#             "user_role": t.user_role,
#             "hostel_id": t.hostel_id
#         }

#     recipients = list(users.values())
#     batch.total_recipients = len(recipients)

#     sent, failed = 0, 0

#     for u in recipients:
#         log = NotificationLog(
#             user_id=u["user_id"],
#             user_role=u["user_role"],
#             hostel_id=u["hostel_id"],
#             notification_type=req.notification_type,
#             title=req.title,
#             body=req.body,
#             data=req.data,
#             priority=req.priority,
#             status=NotificationStatus.pending,
#             created_by=req.created_by,
#             created_by_role=req.created_by_role
#         )
#         db.add(log)
#         db.commit()
#         db.refresh(log)

#         tokens = db.query(DeviceToken).filter(
#             DeviceToken.user_id == u["user_id"],
#             DeviceToken.is_active == True
#         ).all()

#         success = False
#         for tkn in tokens:
#             msg_id, err = await send_fcm_notification(
#                 tkn.device_token, req.title, req.body, req.data, req.priority
#             )
#             if msg_id:
#                 success = True
#                 log.status = NotificationStatus.sent
#                 log.sent_at = datetime.utcnow()

#         if success:
#             sent += 1
#         else:
#             log.status = NotificationStatus.failed
#             failed += 1

#         db.commit()

#     batch.sent_count = sent
#     batch.failed_count = failed
#     batch.completed_at = datetime.utcnow()
#     db.commit()

#     return {
#         "batch_id": batch.id,
#         "total": batch.total_recipients,
#         "sent": sent,
#         "failed": failed
#     }


# # ============================================================
# # USER NOTIFICATION LOGS
# # ============================================================

# @router.get("/user/{user_id}", response_model=List[NotificationLogResponse])
# def get_user_logs(user_id: int, db: Session = Depends(get_db)):
#     return db.query(NotificationLog).filter(
#         NotificationLog.user_id == user_id
#     ).order_by(NotificationLog.created_at.desc()).all()


# @router.put("/{notification_id}/read")
# def mark_read(notification_id: int, db: Session = Depends(get_db)):
#     n = db.query(NotificationLog).filter(NotificationLog.id == notification_id).first()
#     if not n:
#         raise HTTPException(404, "Not found")
#     n.status = NotificationStatus.read
#     n.read_at = datetime.utcnow()
#     db.commit()
#     return {"message": "Marked as read"}


# # ============================================================
# # PREFERENCES
# # ============================================================

# @router.get("/preferences/{user_id}")
# def get_preferences(user_id: int, db: Session = Depends(get_db)):
#     pref = db.query(NotificationPreference).filter(
#         NotificationPreference.user_id == user_id
#     ).first()

#     if not pref:
#         return {"user_id": user_id, "default": True}

#     return pref


# @router.put("/preferences/{user_id}")
# def update_pref(
#     user_id: int,
#     payload: NotificationPreferenceUpdate,
#     db: Session = Depends(get_db)
# ):
#     pref = db.query(NotificationPreference).filter(
#         NotificationPreference.user_id == user_id
#     ).first()

#     if not pref:
#         pref = NotificationPreference(user_id=user_id)
#         db.add(pref)

#     for k, v in payload.dict(exclude_unset=True).items():
#         setattr(pref, k, v)

#     db.commit()
#     db.refresh(pref)
#     return pref
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.config import get_db
from app.models.push_models import (
    DeviceToken, NotificationTemplate, NotificationLog,
    NotificationPreference, NotificationBatch, NotificationType,
    NotificationStatus, UserRole, TargetAudience
)
from app.schemas.push_schemas import *
from app.utils.push_utils import render_template
from app.services.push_services import send_fcm_notification

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Push Notifications"])


# ============================================================
# DEVICE TOKENS (Open for all users)
# ============================================================
@router.post("/device-tokens/", response_model=DeviceTokenResponse)
def register_token(
    payload: DeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT
        ])
    ),
):
    existing = db.query(DeviceToken).filter(
        DeviceToken.device_token == payload.device_token
    ).first()

    if existing:
        for k, v in payload.dict().items():
            setattr(existing, k, v)
        existing.is_active = True
        existing.last_used = datetime.utcnow()
        db.commit()
        return existing

    token = DeviceToken(**payload.dict())
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


# ============================================================
# TEMPLATE CRUD
# ============================================================

@router.post("/templates/", response_model=NotificationTemplateResponse)
def create_template(
    payload: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_NOTIFICATIONS)),
):
    template = NotificationTemplate(**payload.dict())
    db.add(template)
    db.commit()
    return template


@router.get("/templates/", response_model=List[NotificationTemplateResponse])
def list_templates(
    notification_type: Optional[NotificationType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_NOTIFICATIONS)),
):
    q = db.query(NotificationTemplate).filter(NotificationTemplate.is_active == True)
    if notification_type:
        q = q.filter(NotificationTemplate.notification_type == notification_type)
    return q.all()


# ============================================================
# SEND INDIVIDUAL NOTIFICATIONS
# ============================================================
@router.post("/send/")
async def send_notification(
    req: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_NOTIFICATIONS)),
):
    title, body = req.title, req.body

    # Template usage
    if req.template_name:
        t = db.query(NotificationTemplate).filter(
            NotificationTemplate.name == req.template_name
        ).first()
        if not t:
            raise HTTPException(404, "Template not found")

        title = render_template(t.title_template, req.variables)
        body = render_template(t.body_template, req.variables)

    # Determine recipients
    users = []
    if req.user_ids:
        for uid in req.user_ids:
            users.append({
                "user_id": uid,
                "user_role": req.user_role or UserRole.student,
                "hostel_id": None
            })

    # No recipients?
    if not users:
        raise HTTPException(400, "No recipients")

    sent, failed = 0, 0

    for u in users:
        log = NotificationLog(
            user_id=u["user_id"],
            user_role=u["user_role"],
            hostel_id=u["hostel_id"],
            notification_type=req.notification_type,
            title=title,
            body=body,
            priority=req.priority,
            status=NotificationStatus.pending,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        # Send FCM message
        tokens = db.query(DeviceToken).filter(
            DeviceToken.user_id == u["user_id"],
            DeviceToken.is_active == True
        ).all()

        if not tokens:
            log.status = NotificationStatus.failed
            log.error_message = "No active tokens"
            db.commit()
            failed += 1
            continue

        success = False

        for tkn in tokens:
            msg_id, err = await send_fcm_notification(
                tkn.device_token,
                title,
                body,
                req.data,
                req.priority
            )

            if msg_id:
                success = True
                log.fcm_message_id = msg_id
                log.status = NotificationStatus.sent
                log.sent_at = datetime.utcnow()
            else:
                if "not-found" in str(err).lower() or "invalid" in str(err).lower():
                    tkn.is_active = False

        db.commit()

        if success:
            sent += 1
        else:
            failed += 1

    return {
        "total": len(users),
        "sent": sent,
        "failed": failed
    }


# ============================================================
# BROADCAST NOTIFICATIONS
# ============================================================
@router.post("/broadcast/")
async def broadcast(
    req: BroadcastNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.ADMIN, Role.SUPERADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_NOTIFICATIONS)),
):
    batch = NotificationBatch(
        batch_name=f"{req.notification_type.value}_{datetime.utcnow().timestamp()}",
        notification_type=req.notification_type,
        target_audience=req.target_audience,
        hostel_ids=req.hostel_ids,
        user_ids=req.user_ids,
        created_by=req.created_by,
        created_by_role=req.created_by_role
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Determine audience
    q = db.query(DeviceToken).filter(DeviceToken.is_active == True)

    if req.target_audience == TargetAudience.specific_hostel:
        q = q.filter(DeviceToken.hostel_id.in_(req.hostel_ids))

    if req.target_audience == TargetAudience.specific_users:
        q = q.filter(DeviceToken.user_id.in_(req.user_ids))

    if req.target_audience == TargetAudience.all_students:
        q = q.filter(DeviceToken.user_role == UserRole.student)

    recipients = list({t.user_id: t for t in q.all()}.values())
    batch.total_recipients = len(recipients)

    sent, failed = 0, 0

    for t in recipients:
        log = NotificationLog(
            user_id=t.user_id,
            user_role=t.user_role,
            hostel_id=t.hostel_id,
            notification_type=req.notification_type,
            title=req.title,
            body=req.body,
            data=req.data,
            priority=req.priority,
            status=NotificationStatus.pending,
        )
        db.add(log)
        db.commit()

        # Try sending
        msg_id, err = await send_fcm_notification(
            t.device_token,
            req.title,
            req.body,
            req.data,
            req.priority
        )

        if msg_id:
            log.status = NotificationStatus.sent
            log.sent_at = datetime.utcnow()
            sent += 1
        else:
            log.status = NotificationStatus.failed
            failed += 1

        db.commit()

    batch.sent_count = sent
    batch.failed_count = failed
    batch.completed_at = datetime.utcnow()
    db.commit()

    return {
        "batch_id": batch.id,
        "total": batch.total_recipients,
        "sent": sent,
        "failed": failed
    }


# ============================================================
# USER NOTIFICATION LOGS (Student must access own only)
# ============================================================
@router.get("/user/{user_id}", response_model=List[NotificationLogResponse])
def get_user_logs(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR, Role.STUDENT
        ])
    ),
):
    # Student: only own logs
    if current_user.role == Role.STUDENT and current_user.id != user_id:
        raise HTTPException(403, "Access denied")

    return (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id)
        .order_by(NotificationLog.created_at.desc())
        .all()
    )


# ============================================================
# MARK AS READ
# ============================================================
# @router.put("/{notification_id}/read")
# def mark_read(
#     notification_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(
#         role_required([
#             Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR, Role.STUDENT
#         ])
#     ),
# ):
#     n = db.query(NotificationLog).filter(NotificationLog.id == notification_id).first()
#     if not n:
#         raise HTTPException(404, "Not found")

#     # Students can only mark their own notifications
#     if current_user.role == Role.STUDENT and n.user_id != current_user.id:
#         raise HTTPException(403, "Access denied")

#     n.status = NotificationStatus.read
#     n.read_at = datetime.utcnow()
#     db.commit()
#     return {"message": "Marked as read"}


# ============================================================
# USER PREFERENCES (Student must update own only)
# ============================================================
@router.get("/preferences/{user_id}")
def get_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR, Role.STUDENT
        ])
    ),
):
    if current_user.role == Role.STUDENT and current_user.id != user_id:
        raise HTTPException(403, "Access denied")

    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()

    if not pref:
        return {"user_id": user_id, "default": True}

    return pref


@router.put("/preferences/{user_id}")
def update_pref(
    user_id: int,
    payload: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR, Role.STUDENT
        ])
    ),
):
    if current_user.role == Role.STUDENT and current_user.id != user_id:
        raise HTTPException(403, "Access denied")

    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()

    if not pref:
        pref = NotificationPreference(user_id=user_id)
        db.add(pref)

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(pref, k, v)

    db.commit()
    db.refresh(pref)
    return pref
