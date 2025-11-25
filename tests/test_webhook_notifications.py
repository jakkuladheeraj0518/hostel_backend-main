from fastapi.testclient import TestClient

from app.main import app
from app.services.notification_service import NotificationService


client = TestClient(app)


def test_sendgrid_webhook_empty():
    r = client.post("/api/v1/webhooks/notifications/sendgrid", data="")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "skipped": True}


def test_sendgrid_webhook_valid(monkeypatch):
    called = []

    def fake_mark_delivered(db, message_id):
        called.append(message_id)

    monkeypatch.setattr(NotificationService, "mark_delivered", fake_mark_delivered)

    payload = [
        {"sg_message_id": "msg_1", "event": "delivered"},
        {"sg_message_id": "msg_2", "event": "delivered"},
    ]

    r = client.post("/api/v1/webhooks/notifications/sendgrid", json=payload)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert "msg_1" in called and "msg_2" in called
