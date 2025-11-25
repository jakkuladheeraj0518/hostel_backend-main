import pytest

from app.models.notification import NotificationTemplate
from app.models.notification import Notification, DeviceToken, NotificationStatus


def test_notification_template_accepts_subject_and_body():
    t = NotificationTemplate(name="welcome_email", channel="email", subject="Welcome!", body="Hello")
    assert t.name == "welcome_email"
    assert t.channel == "email"
    assert t.subject == "Welcome!"
    assert t.body == "Hello"


def test_notification_template_rejects_old_keyword_args():
    # confirm passing old keywords raises TypeError (keeps behavior explicit)
    with pytest.raises(TypeError):
        NotificationTemplate(name="x", channel="email", subject_template="S", body_template="B")


def test_notification_accepts_status_and_rejects_sent_kw():
    n = Notification(
        recipient_id="user@example.com",
        recipient_type="student",
        channel="email",
        subject="Hi",
        body="Hello",
        status=NotificationStatus.pending.value,
    )
    assert n.status == NotificationStatus.pending.value

    with pytest.raises(TypeError):
        Notification(recipient_id="a", recipient_type="s", channel="email", body="b", sent=True)


def test_device_token_accepts_device_token_and_rejects_token_kw():
    d = DeviceToken(user_id=1, device_token="fcm123", platform="android")
    assert d.device_token == "fcm123"

    with pytest.raises(TypeError):
        DeviceToken(user_id=1, token="fcm123", platform="android")
