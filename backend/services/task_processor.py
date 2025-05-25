import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import crud
from .notification import notification_service

class TaskProcessor:
    def __init__(self):
        self.running = False
        self.tasks = []
        self.db = SessionLocal()
    
    async def start(self):
        """Start the task processor"""
        self.running = True
        self.tasks = [
            asyncio.create_task(self.process_reminders()),
            asyncio.create_task(self.generate_daily_reports()),
            asyncio.create_task(self.cleanup_old_records()),
            asyncio.create_task(self.check_upcoming_appointments())
        ]
        await asyncio.gather(*self.tasks)
    
    async def stop(self):
        """Stop the task processor"""
        self.running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.db.close()
    
    async def process_reminders(self):
        """Process pending reminders"""
        while self.running:
            try:
                # Get pending reminders
                reminders = crud.reminder.get_pending_reminders(self.db)
                
                for reminder in reminders:
                    if reminder.reminder_type == "appointment":
                        success = notification_service.send_appointment_reminder(
                            reminder.appointment_id,
                            reminder.id,
                            self.db
                        )
                    elif reminder.reminder_type == "follow_up":
                        success = notification_service.send_follow_up_reminder(
                            reminder.medical_record_id,
                            reminder.id,
                            self.db
                        )
                    
                    if not success:
                        crud.reminder.mark_reminder_failed(
                            self.db,
                            reminder.id,
                            "Failed to send notification"
                        )
                
                # Wait for 5 minutes before next check
                await asyncio.sleep(300)
            except Exception as e:
                print(f"Error processing reminders: {str(e)}")
                await asyncio.sleep(60)
    
    async def generate_daily_reports(self):
        """Generate daily reports"""
        while self.running:
            try:
                # Check if it's time to generate reports (e.g., at 6 AM)
                now = datetime.now()
                if now.hour == 6 and now.minute == 0:
                    # Generate appointment statistics
                    appointment_stats = crud.appointment.get_appointment_stats(self.db)
                    
                    # Generate patient statistics
                    patient_stats = crud.patient.get_patient_stats(self.db)
                    
                    # Generate reminder statistics
                    reminder_stats = crud.reminder.get_reminder_stats(self.db)
                    
                    # Send reports to administrators
                    admins = crud.user.get_users_by_role(self.db, "admin")
                    for admin in admins:
                        if admin.email:
                            notification_service.send_email(
                                admin.email,
                                "Daily System Report",
                                "daily_report",
                                {
                                    "date": now.strftime("%Y-%m-%d"),
                                    "appointment_stats": appointment_stats,
                                    "patient_stats": patient_stats,
                                    "reminder_stats": reminder_stats
                                }
                            )
                
                # Wait for 1 minute before next check
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error generating daily reports: {str(e)}")
                await asyncio.sleep(60)
    
    async def cleanup_old_records(self):
        """Clean up old records"""
        while self.running:
            try:
                # Check if it's time to clean up (e.g., at 2 AM)
                now = datetime.now()
                if now.hour == 2 and now.minute == 0:
                    # Archive old medical records (older than 7 years)
                    archive_date = now - timedelta(days=365 * 7)
                    crud.medical_record.archive_old_records(self.db, archive_date)
                    
                    # Delete old reminders (older than 1 year)
                    delete_date = now - timedelta(days=365)
                    crud.reminder.delete_old_reminders(self.db, delete_date)
                    
                    # Archive old appointments (older than 2 years)
                    archive_date = now - timedelta(days=365 * 2)
                    crud.appointment.archive_old_appointments(self.db, archive_date)
                
                # Wait for 1 minute before next check
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error cleaning up old records: {str(e)}")
                await asyncio.sleep(60)
    
    async def check_upcoming_appointments(self):
        """Check for upcoming appointments and send notifications"""
        while self.running:
            try:
                # Get appointments for the next 24 hours
                tomorrow = datetime.now() + timedelta(days=1)
                appointments = crud.appointment.get_upcoming_appointments(self.db, 1)
                
                for appointment in appointments:
                    # Check if reminder was already sent
                    if not crud.reminder.has_reminder_been_sent(
                        self.db,
                        appointment.id,
                        "appointment"
                    ):
                        # Create and send reminder
                        reminder = crud.reminder.create_reminder(
                            self.db,
                            {
                                "reminder_type": "appointment",
                                "appointment_id": appointment.id,
                                "scheduled_for": appointment.scheduled_at - timedelta(hours=24)
                            }
                        )
                        if reminder:
                            notification_service.send_appointment_reminder(
                                appointment.id,
                                reminder.id,
                                self.db
                            )
                
                # Wait for 15 minutes before next check
                await asyncio.sleep(900)
            except Exception as e:
                print(f"Error checking upcoming appointments: {str(e)}")
                await asyncio.sleep(60)

# Create singleton instance
task_processor = TaskProcessor()

async def start_task_processor():
    """Start the task processor"""
    await task_processor.start()

async def stop_task_processor():
    """Stop the task processor"""
    await task_processor.stop() 