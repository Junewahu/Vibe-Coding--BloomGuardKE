from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

from ..models.reminder import (
    Reminder, ReminderResponse, ReminderTemplate,
    ReminderDeliveryLog, ReminderProvider,
    ReminderChannel, ReminderStatus, ReminderPriority
)

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.providers: Dict[ReminderChannel, ReminderProvider] = {}

    async def create_reminder(self, db: Session, reminder_data: Dict[str, Any]) -> Reminder:
        """Create a new reminder."""
        reminder = Reminder(**reminder_data)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    async def get_reminder(self, db: Session, reminder_id: int) -> Optional[Reminder]:
        """Get a reminder by ID."""
        return db.query(Reminder).filter(Reminder.id == reminder_id).first()

    async def update_reminder(self, db: Session, reminder_id: int, reminder_data: Dict[str, Any]) -> Optional[Reminder]:
        """Update a reminder."""
        reminder = await self.get_reminder(db, reminder_id)
        if not reminder:
            return None

        for key, value in reminder_data.items():
            setattr(reminder, key, value)

        db.commit()
        db.refresh(reminder)
        return reminder

    async def get_reminders(
        self,
        db: Session,
        schedule_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status: Optional[ReminderStatus] = None,
        channel: Optional[ReminderChannel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Reminder]:
        """Get reminders with filters."""
        query = db.query(Reminder)

        if schedule_id:
            query = query.filter(Reminder.schedule_id == schedule_id)
        if patient_id:
            query = query.filter(Reminder.patient_id == patient_id)
        if status:
            query = query.filter(Reminder.status == status)
        if channel:
            query = query.filter(Reminder.channel == channel)
        if start_date:
            query = query.filter(Reminder.scheduled_time >= start_date)
        if end_date:
            query = query.filter(Reminder.scheduled_time <= end_date)

        return query.all()

    async def create_reminder_response(
        self,
        db: Session,
        reminder_id: int,
        response_data: Dict[str, Any]
    ) -> ReminderResponse:
        """Create a reminder response."""
        response = ReminderResponse(
            reminder_id=reminder_id,
            **response_data
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response

    async def create_template(self, db: Session, template_data: Dict[str, Any]) -> ReminderTemplate:
        """Create a new reminder template."""
        template = ReminderTemplate(**template_data)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    async def get_template(self, db: Session, template_id: int) -> Optional[ReminderTemplate]:
        """Get a template by ID."""
        return db.query(ReminderTemplate).filter(ReminderTemplate.id == template_id).first()

    async def update_template(self, db: Session, template_id: int, template_data: Dict[str, Any]) -> Optional[ReminderTemplate]:
        """Update a template."""
        template = await self.get_template(db, template_id)
        if not template:
            return None

        for key, value in template_data.items():
            setattr(template, key, value)

        db.commit()
        db.refresh(template)
        return template

    async def create_provider(self, db: Session, provider_data: Dict[str, Any]) -> ReminderProvider:
        """Create a new reminder provider."""
        provider = ReminderProvider(**provider_data)
        db.add(provider)
        db.commit()
        db.refresh(provider)
        self.providers[provider.channel] = provider
        return provider

    async def get_provider(self, db: Session, provider_id: int) -> Optional[ReminderProvider]:
        """Get a provider by ID."""
        return db.query(ReminderProvider).filter(ReminderProvider.id == provider_id).first()

    async def update_provider(self, db: Session, provider_id: int, provider_data: Dict[str, Any]) -> Optional[ReminderProvider]:
        """Update a provider."""
        provider = await self.get_provider(db, provider_id)
        if not provider:
            return None

        for key, value in provider_data.items():
            setattr(provider, key, value)

        db.commit()
        db.refresh(provider)
        self.providers[provider.channel] = provider
        return provider

    async def log_delivery_attempt(
        self,
        db: Session,
        reminder_id: int,
        attempt_number: int,
        status: ReminderStatus,
        error_message: Optional[str] = None,
        provider_response: Optional[Dict[str, Any]] = None
    ) -> ReminderDeliveryLog:
        """Log a reminder delivery attempt."""
        reminder = await self.get_reminder(db, reminder_id)
        if not reminder:
            raise ValueError("Reminder not found")

        log = ReminderDeliveryLog(
            reminder_id=reminder_id,
            attempt_number=attempt_number,
            channel=reminder.channel,
            status=status,
            error_message=error_message,
            provider_response=provider_response
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    async def process_pending_reminders(self, db: Session) -> List[Tuple[Reminder, bool]]:
        """Process pending reminders and attempt delivery."""
        now = datetime.utcnow()
        pending_reminders = db.query(Reminder).filter(
            and_(
                Reminder.status == ReminderStatus.PENDING,
                Reminder.scheduled_time <= now,
                Reminder.retry_count < Reminder.max_retries
            )
        ).all()

        results = []
        for reminder in pending_reminders:
            try:
                success = await self.send_reminder(db, reminder)
                results.append((reminder, success))
            except Exception as e:
                logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
                results.append((reminder, False))

        return results

    async def send_reminder(self, db: Session, reminder: Reminder) -> bool:
        """Send a reminder through the appropriate channel."""
        provider = self.providers.get(reminder.channel)
        if not provider or not provider.active:
            raise ValueError(f"No active provider for channel {reminder.channel}")

        try:
            # Update reminder status
            reminder.status = ReminderStatus.SENT
            reminder.sent_time = datetime.utcnow()
            reminder.retry_count += 1
            db.commit()

            # Log delivery attempt
            await self.log_delivery_attempt(
                db,
                reminder.id,
                reminder.retry_count,
                ReminderStatus.SENT
            )

            # TODO: Implement actual delivery through provider
            # This would involve calling the provider's API
            # For now, we'll simulate successful delivery
            reminder.status = ReminderStatus.DELIVERED
            reminder.delivered_time = datetime.utcnow()
            db.commit()

            return True
        except Exception as e:
            logger.error(f"Error sending reminder {reminder.id}: {str(e)}")
            reminder.status = ReminderStatus.FAILED
            reminder.error_message = str(e)
            db.commit()

            # Log failed attempt
            await self.log_delivery_attempt(
                db,
                reminder.id,
                reminder.retry_count,
                ReminderStatus.FAILED,
                error_message=str(e)
            )

            return False

    async def get_reminder_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive reminder statistics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Get reminders
        reminders = await self.get_reminders(
            db,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate statistics
        total_reminders = len(reminders)
        pending_reminders = len([r for r in reminders if r.status == ReminderStatus.PENDING])
        sent_reminders = len([r for r in reminders if r.status == ReminderStatus.SENT])
        delivered_reminders = len([r for r in reminders if r.status == ReminderStatus.DELIVERED])
        failed_reminders = len([r for r in reminders if r.status == ReminderStatus.FAILED])

        # Calculate delivery rate
        delivery_rate = (delivered_reminders / total_reminders * 100) if total_reminders > 0 else 0

        # Calculate average delivery time
        delivery_times = []
        for reminder in reminders:
            if reminder.sent_time and reminder.delivered_time:
                delivery_time = (reminder.delivered_time - reminder.sent_time).total_seconds()
                delivery_times.append(delivery_time)
        average_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else None

        # Get channel distribution
        channel_distribution = {}
        for reminder in reminders:
            channel = reminder.channel.value
            channel_distribution[channel] = channel_distribution.get(channel, 0) + 1

        # Get recent and upcoming reminders
        recent_reminders = sorted(
            [r for r in reminders if r.status in [ReminderStatus.DELIVERED, ReminderStatus.FAILED]],
            key=lambda x: x.sent_time or x.created_at,
            reverse=True
        )[:5]

        upcoming_reminders = sorted(
            [r for r in reminders if r.status == ReminderStatus.PENDING],
            key=lambda x: x.scheduled_time
        )[:5]

        return {
            "total_reminders": total_reminders,
            "pending_reminders": pending_reminders,
            "sent_reminders": sent_reminders,
            "delivered_reminders": delivered_reminders,
            "failed_reminders": failed_reminders,
            "delivery_rate": delivery_rate,
            "average_delivery_time": average_delivery_time,
            "channel_distribution": channel_distribution,
            "recent_reminders": recent_reminders,
            "upcoming_reminders": upcoming_reminders
        }

# Create a singleton instance
reminder_service = ReminderService() 