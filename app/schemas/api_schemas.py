from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

from app.models.api_models import (
    UserRole,
    NotificationCategory,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    FallbackStrategy,
)

# ============================================================
# TEMPLATE SCHEMAS
# ============================================================

class NotificationTemplateCreate(BaseModel):
    name: str
    category: NotificationCategory

    email_subject: Optional[str] = None
    email_template: Optional[str] = None
    sms_template: Optional[str] = None
    push_title: Optional[str] = None
    push_body: Optional[str] = None
    in_app_template: Optional[str] = None

    enabled_channels: List[str]
    primary_channel: NotificationChannel
    fallback_strategy: FallbackStrategy = FallbackStrategy.none

    variables: Optional[Dict] = {}
    priority: NotificationPriority = NotificationPriority.normal
    requires_routing: bool = False


class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    category: NotificationCategory
    enabled_channels: List[str]
    primary_channel: NotificationChannel
    priority: NotificationPriority
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================
# SEND / BROADCAST SCHEMAS
# ============================================================

class SendNotificationRequest(BaseModel):
    # Recipient info
    user_id: int
    user_role: UserRole
    hostel_id: Optional[int] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None

    # Content
    category: NotificationCategory
    priority: NotificationPriority = NotificationPriority.normal
    template_name: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    variables: Optional[Dict] = {}
    data: Optional[Dict] = {}

    # Channel override
    channels: Optional[List[NotificationChannel]] = None

    # Source
    source_module: Optional[str] = None
    source_reference_id: Optional[int] = None

    # Routing engine
    use_routing_engine: bool = False


class BroadcastNotificationRequest(BaseModel):
    user_ids: Optional[List[int]] = None
    user_role: Optional[UserRole] = None
    hostel_ids: Optional[List[int]] = None

    category: NotificationCategory
    priority: NotificationPriority = NotificationPriority.normal

    template_name: Optional[str] = None
    title: str
    message: str
    variables: Optional[Dict] = {}
    data: Optional[Dict] = {}

    channels: Optional[List[NotificationChannel]] = None

    source_module: Optional[str] = None
    created_by: int
    created_by_role: UserRole


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class UnifiedNotificationResponse(BaseModel):
    id: int
    user_id: int
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    status: NotificationStatus
    channels_attempted: List[str]

    email_status: Optional[str]
    sms_status: Optional[str]
    push_status: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class NotificationLogResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    category: NotificationCategory
    status: NotificationStatus
    channels_attempted: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# USER PREFERENCES
# ============================================================

class UserChannelPreferenceUpdate(BaseModel):
    complaint_channels: Optional[List[str]] = None
    maintenance_channels: Optional[List[str]] = None
    attendance_channels: Optional[List[str]] = None
    payment_channels: Optional[List[str]] = None
    booking_channels: Optional[List[str]] = None
    announcement_channels: Optional[List[str]] = None
    emergency_channels: Optional[List[str]] = None

    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None

    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
