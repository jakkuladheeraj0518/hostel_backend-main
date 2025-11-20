from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.notification import (
	Notification,
	NotificationTemplate,
	DeliveryAttempt,
	DeviceToken,
)


class NotificationRepository:
	def __init__(self, db: Session):
		self.db = db

	def create_notification(self, notification: Notification) -> Notification:
		self.db.add(notification)
		self.db.commit()
		self.db.refresh(notification)
		return notification

	def get_notification(self, notification_id: int) -> Optional[Notification]:
		return self.db.query(Notification).filter(Notification.id == notification_id).one_or_none()

	def list_notifications(self, limit: int = 100) -> List[Notification]:
		return self.db.query(Notification).order_by(Notification.created_at.desc()).limit(limit).all()

	def create_template(self, template: NotificationTemplate) -> NotificationTemplate:
		self.db.add(template)
		self.db.commit()
		self.db.refresh(template)
		return template

	def get_template_by_name(self, name: str) -> Optional[NotificationTemplate]:
		return self.db.query(NotificationTemplate).filter(NotificationTemplate.name == name).one_or_none()

	def get_template(self, template_id: int) -> Optional[NotificationTemplate]:
		return self.db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).one_or_none()

	def list_templates(self, limit: int = 100):
		return self.db.query(NotificationTemplate).order_by(NotificationTemplate.created_at.desc()).limit(limit).all()

	def update_template(self, template: NotificationTemplate, data: dict) -> NotificationTemplate:
		for k, v in data.items():
			setattr(template, k, v)
		self.db.add(template)
		self.db.commit()
		self.db.refresh(template)
		return template

	def delete_template(self, template: NotificationTemplate) -> None:
		self.db.delete(template)
		self.db.commit()

	def create_attempt(self, attempt: DeliveryAttempt) -> DeliveryAttempt:
		self.db.add(attempt)
		self.db.commit()
		self.db.refresh(attempt)
		return attempt

	def save_device_token(self, token: DeviceToken) -> DeviceToken:
		self.db.add(token)
		self.db.commit()
		self.db.refresh(token)
		return token
