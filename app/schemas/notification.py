from datetime import datetime
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field

from app.models.notification import (
    NotificationChannel,
    NotificationStatus,
    NotificationPriority,
)


class NotificationBase(BaseModel):
    hostel_id: Optional[int] = Field(None, example=1)
    recipient_id: str = Field(
        ...,
        example="user@example.com / +911234567890 / device_token",
    )
    recipient_type: str = Field(
        ...,
        example="admin / supervisor / student / visitor",
    )
    channel: NotificationChannel
    subject: Optional[str] = Field(None, example="Payment Reminder")
    body: Optional[str] = Field(
        None,
        example="Hi {{name}}, your payment is due on {{due_date}}.",
    )
    template_name: Optional[str] = Field(None, example="payment_reminder")
    template_data: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"name": "Kishore", "due_date": "2025-12-01"},
    )
    priority: NotificationPriority = NotificationPriority.normal


class NotificationCreate(NotificationBase):
    pass


class NotificationOut(NotificationBase):
    id: int
    status: NotificationStatus
    error_message: Optional[str]
    created_at: datetime
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    provider_message_id: Optional[str]

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str = Field(..., example="payment_reminder")
    channel: NotificationChannel
    subject: Optional[str] = Field(None, example="Payment Reminder for {{name}}")
    body: str = Field(
        ...,
        example="Hi {{name}}, your payment of {{amount}} is due on {{due_date}}.",
    )


class TemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    channel: NotificationChannel
    subject: Optional[str]
    body: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceTokenCreate(BaseModel):
    user_id: int
    device_token: str
    platform: str = Field(..., example="android/ios/web")


class DeviceTokenOut(BaseModel):
    id: int
    user_id: int
    device_token: str
    platform: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime

    class Config:
        from_attributes = True


class BulkNotificationRequest(BaseModel):
    """
    For routing engine: send one logical notification to multiple recipients.
    """

    hostel_id: Optional[int] = None
    channel: NotificationChannel
    subject: Optional[str] = None
    body: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    priority: NotificationPriority = NotificationPriority.normal

    # direct recipients
    recipients: Optional[List[str]] = None

    # hierarchical routing flags
    send_to_admins: bool = False
    send_to_supervisors: bool = False
    send_to_students: bool = False
