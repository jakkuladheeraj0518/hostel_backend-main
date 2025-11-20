"""
Background tasks for report generation and scheduling
Using Celery for async task processing
"""

from celery import Celery
from datetime import date, datetime, timedelta
from typing import Optional
import os

from app.config import get_settings

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    'hostel_analytics',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name='generate_daily_report')
def generate_daily_report_task(hostel_id: int, report_date: str):
    """
    Generate daily report for a hostel
    """
    from app.core.database import SessionLocal
    from app.services.analytics_service import AnalyticsService
    
    db = SessionLocal()
    try:
        service = AnalyticsService(db)
        report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        # Generate various reports
        attendance_report = service.get_attendance_report(
            report_date_obj, 
            report_date_obj, 
            hostel_id
        )
        
        complaint_report = service.get_complaint_report(
            report_date_obj,
            report_date_obj,
            hostel_id
        )
        
        # Store or send report
        print(f"Daily report generated for hostel {hostel_id} on {report_date}")
        
        return {
            "status": "success",
            "hostel_id": hostel_id,
            "date": report_date
        }
    finally:
        db.close()


@celery_app.task(name='generate_weekly_report')
def generate_weekly_report_task(hostel_id: int, week_start: str):
    """
    Generate weekly summary report
    """
    from app.core.database import SessionLocal
    from app.services.analytics_service import AnalyticsService
    
    db = SessionLocal()
    try:
        service = AnalyticsService(db)
        week_start_obj = datetime.strptime(week_start, '%Y-%m-%d').date()
        
        weekly_summary = service.get_weekly_summary(hostel_id, week_start_obj)
        
        print(f"Weekly report generated for hostel {hostel_id} starting {week_start}")
        
        return {
            "status": "success",
            "hostel_id": hostel_id,
            "week_start": week_start
        }
    finally:
        db.close()


@celery_app.task(name='generate_monthly_report')
def generate_monthly_report_task(hostel_id: int, month: int, year: int):
    """
    Generate monthly performance report
    """
    from app.core.database import SessionLocal
    from app.services.analytics_service import AnalyticsService
    from calendar import monthrange
    
    db = SessionLocal()
    try:
        service = AnalyticsService(db)
        
        # Get date range for the month
        days_in_month = monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)
        
        # Generate comprehensive reports
        revenue_report = service.get_revenue_report(start_date, end_date, hostel_id)
        occupancy_report = service.get_occupancy_report(start_date, end_date, hostel_id)
        financial_summary = service.get_financial_summary(start_date, end_date, hostel_id)
        
        print(f"Monthly report generated for hostel {hostel_id} for {year}-{month}")
        
        return {
            "status": "success",
            "hostel_id": hostel_id,
            "month": month,
            "year": year
        }
    finally:
        db.close()


@celery_app.task(name='generate_super_admin_report')
def generate_super_admin_report_task(start_date: str, end_date: str):
    """
    Generate comprehensive report for super admin across all hostels
    """
    from app.core.database import SessionLocal
    from app.services.analytics_service import AnalyticsService
    
    db = SessionLocal()
    try:
        service = AnalyticsService(db)
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate multi-hostel comparison
        comparison = service.get_multi_hostel_comparison(start_date_obj, end_date_obj)
        
        print(f"Super admin report generated for {start_date} to {end_date}")
        
        return {
            "status": "success",
            "start_date": start_date,
            "end_date": end_date
        }
    finally:
        db.close()


@celery_app.task(name='cleanup_old_reports')
def cleanup_old_reports_task():
    """
    Clean up old reports based on retention policy
    """
    from app.core.database import SessionLocal
    from app.models import DailyReport
    
    db = SessionLocal()
    try:
        # Delete reports older than MAX_REPORT_AGE_DAYS
        cutoff_date = date.today() - timedelta(days=settings.MAX_REPORT_AGE_DAYS)
        
        deleted_count = db.query(DailyReport).filter(
            DailyReport.report_date < cutoff_date
        ).delete()
        
        db.commit()
        
        print(f"Cleaned up {deleted_count} old reports")
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
    finally:
        db.close()


@celery_app.task(name='send_report_notifications')
def send_report_notifications_task(report_type: str, hostel_id: int, recipients: list):
    """
    Send email notifications for generated reports
    """
    # Placeholder for email notification logic
    print(f"Sending {report_type} report notifications for hostel {hostel_id}")
    print(f"Recipients: {recipients}")
    
    return {
        "status": "success",
        "report_type": report_type,
        "hostel_id": hostel_id,
        "recipients_count": len(recipients)
    }


# Scheduled tasks configuration
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Setup periodic tasks for automatic report generation
    """
    
    # Generate daily reports every day at 11:59 PM
    sender.add_periodic_task(
        crontab(hour=23, minute=59),
        generate_daily_report_task.s(),
        name='daily-reports-generation'
    )
    
    # Generate weekly reports every Monday at 1:00 AM
    sender.add_periodic_task(
        crontab(hour=1, minute=0, day_of_week=1),
        generate_weekly_report_task.s(),
        name='weekly-reports-generation'
    )
    
    # Generate monthly reports on the 1st of each month at 2:00 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0, day_of_month=1),
        generate_monthly_report_task.s(),
        name='monthly-reports-generation'
    )
    
    # Cleanup old reports every Sunday at 3:00 AM
    sender.add_periodic_task(
        crontab(hour=3, minute=0, day_of_week=0),
        cleanup_old_reports_task.s(),
        name='cleanup-old-reports'
    )


# Helper function to schedule ad-hoc report generation
def schedule_report_generation(report_type: str, **kwargs):
    """
    Schedule a report generation task
    """
    if report_type == 'daily':
        return generate_daily_report_task.delay(
            kwargs.get('hostel_id'),
            kwargs.get('report_date')
        )
    elif report_type == 'weekly':
        return generate_weekly_report_task.delay(
            kwargs.get('hostel_id'),
            kwargs.get('week_start')
        )
    elif report_type == 'monthly':
        return generate_monthly_report_task.delay(
            kwargs.get('hostel_id'),
            kwargs.get('month'),
            kwargs.get('year')
        )
    elif report_type == 'super_admin':
        return generate_super_admin_report_task.delay(
            kwargs.get('start_date'),
            kwargs.get('end_date')
        )
    else:
        raise ValueError(f"Unknown report type: {report_type}")