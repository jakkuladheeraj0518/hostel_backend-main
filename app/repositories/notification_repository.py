from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationDeviceToken,
    NotificationStatus,
)


class NotificationRepository:
    """
    SINGLE repository for:
    - Notifications
    - Templates
    - Device tokens (Push)
    """

    # =====================================================
    # ================ TEMPLATE METHODS ===================
    # =====================================================

    @staticmethod
    def get_template_by_id(
        db: Session,
        template_id: int,
    ) -> Optional[NotificationTemplate]:
        return (
            db.query(NotificationTemplate)
            .filter(NotificationTemplate.id == template_id)
            .first()
        )

    @staticmethod
    def get_template_by_name(
        db: Session,
        name: str,
    ) -> Optional[NotificationTemplate]:
        return (
            db.query(NotificationTemplate)
            .filter(NotificationTemplate.name == name)
            .first()
        )

    @staticmethod
    def list_templates(
        db: Session,
    ) -> List[NotificationTemplate]:
        return (
            db.query(NotificationTemplate)
            .order_by(desc(NotificationTemplate.created_at))
            .all()
        )

    @staticmethod
    def create_template(
        db: Session,
        template: NotificationTemplate,
    ) -> NotificationTemplate:
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def update_template(
        db: Session,
        template: NotificationTemplate,
    ) -> NotificationTemplate:
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def delete_template(
        db: Session,
        template_id: int,
    ) -> bool:
        template = (
            db.query(NotificationTemplate)
            .filter(NotificationTemplate.id == template_id)
            .first()
        )

        if not template:
            return False

        db.delete(template)
        db.commit()
        return True

    # =====================================================
    # ================= NOTIFICATION METHODS ==============
    # =====================================================

    @staticmethod
    def create_notification(
        db: Session,
        notification: Notification,
    ) -> Notification:
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def update_notification(
        db: Session,
        notification: Notification,
    ) -> Notification:
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_by_id(
        db: Session,
        notification_id: int,
    ) -> Optional[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        limit: int = 200,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .order_by(desc(Notification.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_recipient(
        db: Session,
        recipient_id: str,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.recipient_id == recipient_id)
            .order_by(desc(Notification.created_at))
            .all()
        )

    @staticmethod
    def get_by_hostel(
        db: Session,
        hostel_id: int,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.hostel_id == hostel_id)
            .order_by(desc(Notification.created_at))
            .all()
        )

    @staticmethod
    def get_by_role(
        db: Session,
        recipient_type: str,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.recipient_type == recipient_type)
            .order_by(desc(Notification.created_at))
            .all()
        )

    @staticmethod
    def get_failed(
        db: Session,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.status == NotificationStatus.failed.value)
            .order_by(desc(Notification.created_at))
            .all()
        )

    @staticmethod
    def get_pending(
        db: Session,
    ) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.status == NotificationStatus.pending.value)
            .order_by(desc(Notification.created_at))
            .all()
        )

    @staticmethod
    def mark_as_delivered(
        db: Session,
        provider_message_id: str,
    ) -> Optional[Notification]:
        notification = (
            db.query(Notification)
            .filter(Notification.provider_message_id == provider_message_id)
            .first()
        )

        if not notification:
            return None

        notification.status = NotificationStatus.delivered.value
        db.commit()
        db.refresh(notification)
        return notification

    # =====================================================
    # ================= DEVICE TOKEN METHODS ==============
    # =====================================================

    @staticmethod
    def save_device_token(
        db: Session,
        token: NotificationDeviceToken,
    ) -> NotificationDeviceToken:
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_device_by_token(
        db: Session,
        token_value: str,
    ) -> Optional[NotificationDeviceToken]:
        return (
            db.query(NotificationDeviceToken)
            .filter(NotificationDeviceToken.device_token == token_value)
            .first()
        )

    @staticmethod
    def get_devices_for_user(
        db: Session,
        user_id: int,
    ) -> List[NotificationDeviceToken]:
        return (
            db.query(NotificationDeviceToken)
            .filter(NotificationDeviceToken.user_id == user_id)
            .filter(NotificationDeviceToken.is_active == 1)
            .order_by(desc(NotificationDeviceToken.created_at))
            .all()
        )

    @staticmethod
    def deactivate_device(
        db: Session,
        token_value: str,
    ) -> bool:
        token = (
            db.query(NotificationDeviceToken)
            .filter(NotificationDeviceToken.device_token == token_value)
            .first()
        )

        if not token:
            return False

        token.is_active = 0
        db.commit()
        return True

    @staticmethod
    def delete_all_user_devices(
        db: Session,
        user_id: int,
    ) -> int:
        count = (
            db.query(NotificationDeviceToken)
            .filter(NotificationDeviceToken.user_id == user_id)
            .delete()
        )

        db.commit()
        return count
