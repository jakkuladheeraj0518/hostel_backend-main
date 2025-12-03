# app/services/scheduler.py
from datetime import datetime, timedelta
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.rooms import Room

logger = logging.getLogger("hostel_scheduler")
logger.setLevel(logging.INFO)


# --- CONFIG ---
# How old (in hours) a PENDING booking must be to be expired automatically
DEFAULT_EXPIRY_HOURS = 24

# How often the scheduler will run (in seconds). For dev/testing you can set to 60.
DEFAULT_RUN_INTERVAL_SECONDS = 60  # run every minute. Change to 3600 for hourly, etc.
# ---------------


def expire_pending_bookings_once(expiry_hours: int = DEFAULT_EXPIRY_HOURS):
    """
    One-off run: finds bookings with status PENDING older than expiry_hours
    and marks them as rejected. Releases any bed if necessary.
    """
    cutoff = datetime.utcnow() - timedelta(hours=expiry_hours)
    db: Session = SessionLocal()

    expired_count = 0
    try:
        # Find pending bookings older than cutoff
        pending_q = db.query(Booking).filter(
            Booking.status == BookingStatus.pending.value,
            Booking.created_at < cutoff
        )

        pending_list = pending_q.all()

        if not pending_list:
            logger.info("No pending bookings to expire (cutoff=%s)", cutoff.isoformat())
            return {"expired": 0, "cutoff": cutoff.isoformat()}

        for booking in pending_list:
            try:
                # Extra-safety: if booking was somehow confirmed already, skip expiry
                if booking.status != BookingStatus.pending.value:
                    continue

                # mark booking as rejected (store string value)
                booking.status = BookingStatus.rejected.value

                # If the booking had reserved/consumed a bed (shouldn't for pending),
                # ensure bed counts are correct. This is defensive: only decrement/increment
                # when consistent with your app's confirm flow.
                # We'll increment available_beds if booking was confirmed earlier (defensive)
                if booking.room_id:
                    room = db.query(Room).filter(Room.id == booking.room_id).first()
                    if room:
                        # only adjust if available_beds would logically increase
                        # (we don't want available_beds > total_beds; keep defensive checks)
                        try:
                            room.available_beds = min(room.total_beds, (room.available_beds + 1))
                        except Exception:
                            # fallback: try set to total_beds if anything weird
                            room.available_beds = room.total_beds

                # Placeholder: refund handling (if advance was paid & policy allows)
                # call_refund_processor(booking)  -> implement when integrating payment gateway

                db.add(booking)
                expired_count += 1
            except Exception as inner:
                logger.exception("Failed to expire booking id=%s: %s", getattr(booking, "id", None), str(inner))
                db.rollback()
                continue

        db.commit()
        logger.info("Expired %d pending bookings older than %d hours", expired_count, expiry_hours)
        return {"expired": expired_count, "cutoff": cutoff.isoformat()}

    except Exception as e:
        db.rollback()
        logger.exception("Error during expire_pending_bookings_once: %s", str(e))
        raise
    finally:
        db.close()


# Scheduler control API
_scheduler: BackgroundScheduler | None = None


def start_scheduler(interval_seconds: int = DEFAULT_RUN_INTERVAL_SECONDS, expiry_hours: int = DEFAULT_EXPIRY_HOURS):
    """
    Start the background scheduler (idempotent).
    It will run expire_pending_bookings_once every `interval_seconds`.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.info("Scheduler already running")
        return _scheduler

    _scheduler = BackgroundScheduler()
    trigger = IntervalTrigger(seconds=interval_seconds)
    _scheduler.add_job(
        expire_pending_bookings_once,
        trigger,
        args=(expiry_hours,),
        id="expire_pending_bookings_job",
        replace_existing=True,
        max_instances=1,
    )

    _scheduler.start()
    logger.info("Scheduler started: interval_seconds=%s expiry_hours=%s", interval_seconds, expiry_hours)
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None
