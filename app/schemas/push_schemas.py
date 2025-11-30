from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

from app.models.push_models import (
    UserRole, NotificationType, NotificationPriority,
    NotificationStatus, TargetAudience
)


# ============================================================
# DEVICE TOKEN SCHEMAS
# ============================================================

class DeviceTokenCreate(BaseModel):
    user_id: int
    user_role: UserRole
    hostel_id: Optional[int] = None
    device_token: str
    device_type: str
    device_name: Optional[str] = None
    app_version: Optional[str] = None


class DeviceTokenResponse(BaseModel):
    id: int
    user_id: int
    user_role: UserRole
    hostel_id: Optional[int]
    device_token: str
    device_type: str
    is_active: bool
    last_used: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# TEMPLATES
# ============================================================

class NotificationTemplateCreate(BaseModel):
    name: str
    notification_type: NotificationType
    title_template: str
    body_template: str
    data_schema: Optional[Dict] = {}
    priority: NotificationPriority = NotificationPriority.normal
    sound: str = "default"


class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    notification_type: NotificationType
    title_template: str
    body_template: str
    priority: NotificationPriority
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================
# SEND NOTIFICATIONS
# ============================================================

class SendNotificationRequest(BaseModel):
    user_ids: Optional[List[int]] = None
    user_role: Optional[UserRole] = None
    hostel_ids: Optional[List[int]] = None
    title: str
    body: str
    notification_type: NotificationType
    data: Optional[Dict] = {}
    priority: NotificationPriority = NotificationPriority.normal
    template_name: Optional[str] = None
    variables: Optional[Dict] = {}


class BroadcastNotificationRequest(BaseModel):
    target_audience: TargetAudience
    hostel_ids: Optional[List[int]] = None
    room_numbers: Optional[List[str]] = None
    floor_numbers: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None
    title: str
    body: str
    notification_type: NotificationType
    data: Optional[Dict] = {}
    priority: NotificationPriority = NotificationPriority.normal
    created_by: int
    created_by_role: UserRole


# ============================================================
# LOGS
# ============================================================

class NotificationLogResponse(BaseModel):
    id: int
    user_id: int
    user_role: UserRole
    hostel_id: Optional[int]
    notification_type: NotificationType
    title: str
    body: str
    priority: NotificationPriority
    status: NotificationStatus
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PREFERENCES
# ============================================================

class NotificationPreferenceUpdate(BaseModel):
    announcement_enabled: Optional[bool] = None
    payment_reminder_enabled: Optional[bool] = None
    complaint_update_enabled: Optional[bool] = None
    maintenance_update_enabled: Optional[bool] = None
    attendance_alert_enabled: Optional[bool] = None
    booking_update_enabled: Optional[bool] = None
    mess_menu_enabled: Optional[bool] = None
    leave_approval_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# ============================================================
# ROUTING RULES
# ============================================================

class HierarchicalRoutingCreate(BaseModel):
    notification_type: NotificationType
    source_role: UserRole
    requires_admin_approval: bool = False
    route_to_admin: bool = False
    route_to_supervisor: bool = False
    escalation_threshold_hours: Optional[int] = None
    priority_override: Optional[NotificationPriority] = None
