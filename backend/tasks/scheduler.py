from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.escalation import EscalationService
from ..services.notification import NotificationService
from ..services.scheduling import SchedulingService
import asyncio

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._init_tasks()

    def _init_tasks(self):
        """Initialize scheduled tasks"""
        # Check escalations every hour
        self.scheduler.add_job(
            self._check_escalations,
            IntervalTrigger(hours=1),
            id="check_escalations",
            replace_existing=True
        )
        
        # Send pending notifications every 5 minutes
        self.scheduler.add_job(
            self._send_pending_notifications,
            IntervalTrigger(minutes=5),
            id="send_notifications",
            replace_existing=True
        )
        
        # Clean up old notifications daily at midnight
        self.scheduler.add_job(
            self._cleanup_old_notifications,
            CronTrigger(hour=0, minute=0),
            id="cleanup_notifications",
            replace_existing=True
        )
        
        # Generate daily reports at 1 AM
        self.scheduler.add_job(
            self._generate_daily_reports,
            CronTrigger(hour=1, minute=0),
            id="daily_reports",
            replace_existing=True
        )
        
        # Check for upcoming appointments every 30 minutes
        self.scheduler.add_job(
            self._check_upcoming_appointments,
            IntervalTrigger(minutes=30),
            id="check_appointments",
            replace_existing=True
        )

    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Task scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting task scheduler: {str(e)}")
            raise

    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Task scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down task scheduler: {str(e)}")
            raise

    async def _check_escalations(self):
        """Check for cases that need escalation"""
        try:
            db = SessionLocal()
            try:
                escalation_service = EscalationService(db)
                await escalation_service.check_escalations()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error checking escalations: {str(e)}")

    async def _send_pending_notifications(self):
        """Send pending notifications"""
        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                
                # Get pending notifications
                pending_notifications = await notification_service.get_pending_notifications()
                
                for notification in pending_notifications:
                    try:
                        # Send notification
                        await notification_service.send_notification(notification)
                        
                        # Update status
                        await notification_service.update_notification_status(
                            notification.id,
                            "sent"
                        )
                    except Exception as e:
                        logger.error(f"Error sending notification {notification.id}: {str(e)}")
                        # Update status to failed
                        await notification_service.update_notification_status(
                            notification.id,
                            "failed",
                            {"error": str(e)}
                        )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error sending pending notifications: {str(e)}")

    async def _cleanup_old_notifications(self):
        """Clean up old notifications"""
        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                
                # Get notifications older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                old_notifications = await notification_service.get_notifications(
                    created_before=cutoff_date
                )
                
                for notification in old_notifications:
                    try:
                        # Archive notification
                        await notification_service.archive_notification(notification.id)
                    except Exception as e:
                        logger.error(f"Error archiving notification {notification.id}: {str(e)}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {str(e)}")

    async def _generate_daily_reports(self):
        """Generate daily reports"""
        try:
            db = SessionLocal()
            try:
                # Get notification stats
                notification_service = NotificationService(db)
                notification_stats = await notification_service.get_notification_stats()
                
                # Get scheduling stats
                scheduling_service = SchedulingService(db)
                scheduling_stats = await scheduling_service.get_schedule_stats()
                
                # TODO: Implement report generation and distribution
                logger.info("Daily reports generated successfully")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error generating daily reports: {str(e)}")

    async def _check_upcoming_appointments(self):
        """Check for upcoming appointments"""
        try:
            db = SessionLocal()
            try:
                scheduling_service = SchedulingService(db)
                notification_service = NotificationService(db)
                
                # Get appointments in the next 24 hours
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(hours=24)
                
                upcoming_appointments = await scheduling_service.get_follow_up_schedules(
                    start_date=start_date,
                    end_date=end_date,
                    status="pending"
                )
                
                for appointment in upcoming_appointments:
                    try:
                        # Create reminder notification
                        notification = await notification_service.create_notification(
                            patient_id=appointment.patient_id,
                            channel="whatsapp",  # or based on patient preference
                            template_type="appointment_reminder",
                            metadata={
                                "appointment_id": appointment.id,
                                "appointment_date": appointment.start_date.isoformat(),
                                "appointment_type": appointment.schedule_type
                            }
                        )
                        
                        # Schedule notification
                        await notification_service.schedule_notification(
                            notification.id,
                            appointment.start_date - timedelta(hours=24)
                        )
                    except Exception as e:
                        logger.error(f"Error creating reminder for appointment {appointment.id}: {str(e)}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error checking upcoming appointments: {str(e)}")

# Create global scheduler instance
scheduler = TaskScheduler()

def start_scheduler():
    """Start the task scheduler"""
    scheduler.start()

def shutdown_scheduler():
    """Shutdown the task scheduler"""
    scheduler.shutdown() 