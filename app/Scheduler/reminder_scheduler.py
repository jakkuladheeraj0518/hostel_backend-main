# app/scheduler/reminder_scheduler.py

from app.Scheduler.reminder_scheduler import BackgroundScheduler
from app.Scheduler.reminder_scheduler import CronTrigger
from app.core.database import SessionLocal
from app.services.reminder_services import process_automated_reminders

scheduler = BackgroundScheduler()


def start_scheduler():

    scheduler.add_job(
        run_reminder_job,
        CronTrigger(minute="0"),   # Every hour on the hour
        id="hourly_reminder_job",
        replace_existing=True
    )

    scheduler.add_job(
        run_reminder_job,
        CronTrigger(hour="9", minute="0"),  # Every day 9 AM
        id="daily_reminder_job",
        replace_existing=True
    )

    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)


def run_reminder_job():
    db = SessionLocal()
    try:
        process_automated_reminders(db)
    finally:
        db.close()
