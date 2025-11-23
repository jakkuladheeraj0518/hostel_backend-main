"""Simple background dispatcher for notifications using a worker thread and queue.
 
This is a lightweight alternative to Celery for demo and testing.
"""
from queue import Queue, Empty
from threading import Thread
import time
from typing import Dict, Any
 
from app.core.database import SessionLocal
 
_queue: "Queue[Dict[str, Any]]" = Queue()
_worker_started = False
 
 
def _worker():
    db = SessionLocal()
    # Import here to avoid circular imports at module import time
    from app.services.notification_service import NotificationService
    svc = NotificationService(db)
    while True:
        try:
            job = _queue.get(timeout=1)
        except Empty:
            continue
        try:
            svc._perform_send(job["notification_id"])
        except Exception:
            # TODO: add retry/backoff
            pass
        finally:
            _queue.task_done()
 
 
def start_worker():
    global _worker_started
    if not _worker_started:
        t = Thread(target=_worker, daemon=True)
        t.start()
        _worker_started = True
 
 
def enqueue_send(notification_id: int):
    start_worker()
    _queue.put({"notification_id": notification_id})