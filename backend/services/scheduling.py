from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

from ..models.scheduling import (
    ScheduleRule,
    Schedule,
    ScheduleReminder,
    ScheduleTemplate,
    ScheduleOverride,
    ScheduleType,
    ScheduleStatus,
    CustomProtocol,
    FollowUpSchedule,
    ScheduleAdjustment
)
from ..models.calendar import CalendarEvent, EventType
from ..schemas.scheduling import (
    ScheduleRuleCreate,
    ScheduleRuleUpdate,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleReminderCreate,
    ScheduleReminderUpdate,
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate,
    ScheduleOverrideCreate,
    CustomProtocolCreate,
    CustomProtocolUpdate,
    FollowUpScheduleCreate,
    FollowUpScheduleUpdate,
    ScheduleAdjustmentCreate,
    ScheduleAdjustmentUpdate
)

logger = logging.getLogger(__name__)

class SchedulingService:
    def __init__(self, db: Session):
        self.db = db

    # Schedule Rule methods
    def create_schedule_rule(self, rule: ScheduleRuleCreate, user_id: int) -> ScheduleRule:
        """Create a new schedule rule"""
        try:
            db_rule = ScheduleRule(
                **rule.dict(),
                created_by=user_id
            )
            self.db.add(db_rule)
            self.db.commit()
            self.db.refresh(db_rule)
            return db_rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating schedule rule: {str(e)}")
            raise

    def update_schedule_rule(self, rule_id: int, rule: ScheduleRuleUpdate) -> Optional[ScheduleRule]:
        """Update an existing schedule rule"""
        try:
            db_rule = self.db.query(ScheduleRule).filter(ScheduleRule.id == rule_id).first()
            if not db_rule:
                return None

            update_data = rule.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_rule, field, value)

            self.db.commit()
            self.db.refresh(db_rule)
            return db_rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating schedule rule: {str(e)}")
            raise

    def get_schedule_rules(
        self,
        rule_type: Optional[ScheduleType] = None,
        is_active: Optional[bool] = None
    ) -> List[ScheduleRule]:
        """Get schedule rules with optional filters"""
        query = self.db.query(ScheduleRule)
        
        if rule_type:
            query = query.filter(ScheduleRule.rule_type == rule_type)
        if is_active is not None:
            query = query.filter(ScheduleRule.is_active == is_active)
            
        return query.all()

    # Custom Protocol methods
    def create_custom_protocol(self, protocol: CustomProtocolCreate, user_id: int) -> CustomProtocol:
        """Create a new custom protocol"""
        try:
            db_protocol = CustomProtocol(
                **protocol.dict(),
                created_by=user_id
            )
            self.db.add(db_protocol)
            self.db.commit()
            self.db.refresh(db_protocol)
            return db_protocol
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating custom protocol: {str(e)}")
            raise

    def update_custom_protocol(self, protocol_id: int, protocol: CustomProtocolUpdate) -> Optional[CustomProtocol]:
        """Update an existing custom protocol"""
        try:
            db_protocol = self.db.query(CustomProtocol).filter(CustomProtocol.id == protocol_id).first()
            if not db_protocol:
                return None

            update_data = protocol.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_protocol, field, value)

            self.db.commit()
            self.db.refresh(db_protocol)
            return db_protocol
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating custom protocol: {str(e)}")
            raise

    def get_custom_protocols(
        self,
        protocol_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[CustomProtocol]:
        """Get custom protocols with optional filters"""
        query = self.db.query(CustomProtocol)
        
        if protocol_type:
            query = query.filter(CustomProtocol.protocol_type == protocol_type)
        if is_active is not None:
            query = query.filter(CustomProtocol.is_active == is_active)
            
        return query.all()

    # Follow-Up Schedule methods
    def create_follow_up_schedule(self, schedule: FollowUpScheduleCreate, user_id: int) -> FollowUpSchedule:
        """Create a new follow-up schedule"""
        try:
            db_schedule = FollowUpSchedule(
                **schedule.dict(),
                status=ScheduleStatus.PENDING,
                created_by=user_id
            )
            self.db.add(db_schedule)
            self.db.commit()
            self.db.refresh(db_schedule)
            return db_schedule
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating follow-up schedule: {str(e)}")
            raise

    def update_follow_up_schedule(self, schedule_id: int, schedule: FollowUpScheduleUpdate) -> Optional[FollowUpSchedule]:
        """Update an existing follow-up schedule"""
        try:
            db_schedule = self.db.query(FollowUpSchedule).filter(FollowUpSchedule.id == schedule_id).first()
            if not db_schedule:
                return None

            update_data = schedule.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_schedule, field, value)

            self.db.commit()
            self.db.refresh(db_schedule)
            return db_schedule
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating follow-up schedule: {str(e)}")
            raise

    def get_follow_up_schedules(
        self,
        patient_id: Optional[int] = None,
        schedule_type: Optional[ScheduleType] = None,
        status: Optional[ScheduleStatus] = None
    ) -> List[FollowUpSchedule]:
        """Get follow-up schedules with optional filters"""
        query = self.db.query(FollowUpSchedule)
        
        if patient_id:
            query = query.filter(FollowUpSchedule.patient_id == patient_id)
        if schedule_type:
            query = query.filter(FollowUpSchedule.schedule_type == schedule_type)
        if status:
            query = query.filter(FollowUpSchedule.status == status)
            
        return query.all()

    # Schedule Adjustment methods
    def create_schedule_adjustment(self, adjustment: ScheduleAdjustmentCreate, user_id: int) -> ScheduleAdjustment:
        """Create a new schedule adjustment"""
        try:
            db_adjustment = ScheduleAdjustment(
                **adjustment.dict(),
                created_by=user_id
            )
            self.db.add(db_adjustment)
            self.db.commit()
            self.db.refresh(db_adjustment)
            return db_adjustment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating schedule adjustment: {str(e)}")
            raise

    def update_schedule_adjustment(self, adjustment_id: int, adjustment: ScheduleAdjustmentUpdate) -> Optional[ScheduleAdjustment]:
        """Update an existing schedule adjustment"""
        try:
            db_adjustment = self.db.query(ScheduleAdjustment).filter(ScheduleAdjustment.id == adjustment_id).first()
            if not db_adjustment:
                return None

            update_data = adjustment.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_adjustment, field, value)

            self.db.commit()
            self.db.refresh(db_adjustment)
            return db_adjustment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating schedule adjustment: {str(e)}")
            raise

    def get_schedule_adjustments(
        self,
        schedule_id: Optional[int] = None,
        adjustment_type: Optional[str] = None
    ) -> List[ScheduleAdjustment]:
        """Get schedule adjustments with optional filters"""
        query = self.db.query(ScheduleAdjustment)
        
        if schedule_id:
            query = query.filter(ScheduleAdjustment.schedule_id == schedule_id)
        if adjustment_type:
            query = query.filter(ScheduleAdjustment.adjustment_type == adjustment_type)
            
        return query.all()

    # Statistics methods
    def get_schedule_stats(self) -> Dict[str, Any]:
        """Get scheduling statistics"""
        try:
            total_schedules = self.db.query(func.count(FollowUpSchedule.id)).scalar()
            
            # Get schedules by type
            schedules_by_type = {}
            for schedule_type in ScheduleType:
                count = self.db.query(func.count(FollowUpSchedule.id))\
                    .filter(FollowUpSchedule.schedule_type == schedule_type)\
                    .scalar()
                schedules_by_type[schedule_type.value] = count

            # Get schedules by status
            schedules_by_status = {}
            for status in ScheduleStatus:
                count = self.db.query(func.count(FollowUpSchedule.id))\
                    .filter(FollowUpSchedule.status == status)\
                    .scalar()
                schedules_by_status[status.value] = count

            # Calculate average duration
            avg_duration = self.db.query(
                func.avg(
                    func.extract('epoch', FollowUpSchedule.end_date - FollowUpSchedule.start_date)
                )
            ).scalar() or 0

            # Calculate completion rate
            completed = self.db.query(func.count(FollowUpSchedule.id))\
                .filter(FollowUpSchedule.status == ScheduleStatus.COMPLETED)\
                .scalar()
            completion_rate = (completed / total_schedules * 100) if total_schedules > 0 else 0

            # Get recent adjustments
            recent_adjustments = self.db.query(ScheduleAdjustment)\
                .order_by(ScheduleAdjustment.created_at.desc())\
                .limit(5)\
                .all()

            # Get active protocols
            active_protocols = self.db.query(CustomProtocol)\
                .filter(CustomProtocol.is_active == True)\
                .all()

            # Get popular rules
            popular_rules = self.db.query(ScheduleRule)\
                .filter(ScheduleRule.is_active == True)\
                .all()

            return {
                "total_schedules": total_schedules,
                "schedules_by_type": schedules_by_type,
                "schedules_by_status": schedules_by_status,
                "average_duration": avg_duration,
                "completion_rate": completion_rate,
                "recent_adjustments": recent_adjustments,
                "active_protocols": active_protocols,
                "popular_rules": popular_rules
            }
        except Exception as e:
            logger.error(f"Error getting schedule stats: {str(e)}")
            raise

    async def create_rule(self, db: Session, rule_data: Dict[str, Any]) -> ScheduleRule:
        """Create a new scheduling rule."""
        rule = ScheduleRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    async def get_rule(self, db: Session, rule_id: int) -> Optional[ScheduleRule]:
        """Get a scheduling rule by ID."""
        return db.query(ScheduleRule).filter(ScheduleRule.id == rule_id).first()

    async def update_rule(self, db: Session, rule_id: int, rule_data: Dict[str, Any]) -> Optional[ScheduleRule]:
        """Update a scheduling rule."""
        rule = await self.get_rule(db, rule_id)
        if not rule:
            return None

        for key, value in rule_data.items():
            setattr(rule, key, value)

        db.commit()
        db.refresh(rule)
        return rule

    async def create_schedule(self, db: Session, schedule_data: Dict[str, Any]) -> Schedule:
        """Create a new schedule."""
        schedule = Schedule(**schedule_data)
        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        # Create calendar event for the schedule
        calendar_event = CalendarEvent(
            event_type=EventType.SCHEDULE,
            title=f"Schedule: {schedule.rule.name}",
            description=schedule.notes,
            start_time=schedule.scheduled_date,
            end_time=schedule.scheduled_date + timedelta(hours=1),  # Default 1-hour duration
            schedule_id=schedule.id
        )
        db.add(calendar_event)
        db.commit()

        return schedule

    async def update_schedule(self, db: Session, schedule_id: int, schedule_data: Dict[str, Any]) -> Optional[Schedule]:
        """Update a schedule."""
        schedule = await self.get_schedule(db, schedule_id)
        if not schedule:
            return None

        # Handle rescheduling
        if "scheduled_date" in schedule_data and schedule_data["scheduled_date"] != schedule.scheduled_date:
            schedule_data["original_date"] = schedule.scheduled_date
            schedule_data["reschedule_count"] = schedule.reschedule_count + 1
            schedule_data["status"] = ScheduleStatus.RESCHEDULED

        for key, value in schedule_data.items():
            setattr(schedule, key, value)

        db.commit()
        db.refresh(schedule)

        # Update calendar event
        calendar_event = db.query(CalendarEvent).filter(
            CalendarEvent.schedule_id == schedule.id
        ).first()
        if calendar_event:
            calendar_event.start_time = schedule.scheduled_date
            calendar_event.end_time = schedule.scheduled_date + timedelta(hours=1)
            db.commit()

        return schedule

    async def get_schedule(self, db: Session, schedule_id: int) -> Optional[Schedule]:
        """Get a schedule by ID."""
        return db.query(Schedule).filter(Schedule.id == schedule_id).first()

    async def get_schedules(
        self,
        db: Session,
        patient_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        status: Optional[ScheduleStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Schedule]:
        """Get schedules with filters."""
        query = db.query(Schedule)

        if patient_id:
            query = query.filter(Schedule.patient_id == patient_id)
        if rule_id:
            query = query.filter(Schedule.rule_id == rule_id)
        if status:
            query = query.filter(Schedule.status == status)
        if start_date:
            query = query.filter(Schedule.scheduled_date >= start_date)
        if end_date:
            query = query.filter(Schedule.scheduled_date <= end_date)

        return query.all()

    async def create_reminder(self, db: Session, reminder_data: Dict[str, Any]) -> ScheduleReminder:
        """Create a new schedule reminder."""
        reminder = ScheduleReminder(**reminder_data)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    async def update_reminder(self, db: Session, reminder_id: int, reminder_data: Dict[str, Any]) -> Optional[ScheduleReminder]:
        """Update a schedule reminder."""
        reminder = db.query(ScheduleReminder).filter(ScheduleReminder.id == reminder_id).first()
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
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ScheduleReminder]:
        """Get reminders with filters."""
        query = db.query(ScheduleReminder)

        if schedule_id:
            query = query.filter(ScheduleReminder.schedule_id == schedule_id)
        if status:
            query = query.filter(ScheduleReminder.status == status)
        if start_date:
            query = query.filter(ScheduleReminder.reminder_date >= start_date)
        if end_date:
            query = query.filter(ScheduleReminder.reminder_date <= end_date)

        return query.all()

    async def create_template(self, db: Session, template_data: Dict[str, Any]) -> ScheduleTemplate:
        """Create a new schedule template."""
        template = ScheduleTemplate(**template_data)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    async def update_template(self, db: Session, template_id: int, template_data: Dict[str, Any]) -> Optional[ScheduleTemplate]:
        """Update a schedule template."""
        template = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id).first()
        if not template:
            return None

        for key, value in template_data.items():
            setattr(template, key, value)

        db.commit()
        db.refresh(template)
        return template

    async def create_override(self, db: Session, override_data: Dict[str, Any]) -> ScheduleOverride:
        """Create a new schedule override."""
        override = ScheduleOverride(**override_data)
        db.add(override)
        db.commit()
        db.refresh(override)
        return override

    async def get_schedule_stats(
        self,
        db: Session,
        patient_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive schedule statistics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Get schedules
        schedules = await self.get_schedules(
            db,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate statistics
        total_schedules = len(schedules)
        completed_schedules = len([s for s in schedules if s.status == ScheduleStatus.COMPLETED])
        missed_schedules = len([s for s in schedules if s.status == ScheduleStatus.MISSED])
        upcoming_schedules = len([s for s in schedules if s.status == ScheduleStatus.SCHEDULED])

        # Calculate completion rate
        completion_rate = (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0

        # Get schedule distribution
        schedule_distribution = {}
        for schedule in schedules:
            schedule_type = schedule.rule.schedule_type.value
            schedule_distribution[schedule_type] = schedule_distribution.get(schedule_type, 0) + 1

        # Get recent and upcoming schedules
        recent_schedules = sorted(
            [s for s in schedules if s.status == ScheduleStatus.COMPLETED],
            key=lambda x: x.completed_date,
            reverse=True
        )[:5]

        upcoming_schedules_list = sorted(
            [s for s in schedules if s.status == ScheduleStatus.SCHEDULED],
            key=lambda x: x.scheduled_date
        )[:5]

        # Calculate average response time
        reminders = await self.get_reminders(
            db,
            schedule_id=[s.id for s in schedules],
            status="delivered"
        )
        response_times = []
        for reminder in reminders:
            if reminder.response and "response_time" in reminder.response:
                response_times.append(reminder.response["response_time"])
        average_response_time = sum(response_times) / len(response_times) if response_times else None

        return {
            "total_schedules": total_schedules,
            "completed_schedules": completed_schedules,
            "missed_schedules": missed_schedules,
            "upcoming_schedules": upcoming_schedules,
            "completion_rate": completion_rate,
            "average_response_time": average_response_time,
            "schedule_distribution": schedule_distribution,
            "recent_schedules": recent_schedules,
            "upcoming_schedules_list": upcoming_schedules_list
        }

    async def handle_missed_appointments(self, db: Session) -> List[Schedule]:
        """Handle missed appointments by marking them and creating reschedule events."""
        now = datetime.utcnow()
        missed_schedules = db.query(Schedule).filter(
            and_(
                Schedule.status == ScheduleStatus.SCHEDULED,
                Schedule.scheduled_date < now
            )
        ).all()

        for schedule in missed_schedules:
            schedule.status = ScheduleStatus.MISSED
            db.commit()

            # Create calendar event for missed appointment
            calendar_event = CalendarEvent(
                event_type=EventType.FOLLOW_UP,
                title=f"Missed: {schedule.rule.name}",
                description=f"Missed appointment for {schedule.patient.name}. Please reschedule.",
                start_time=now,
                end_time=now + timedelta(hours=1),
                schedule_id=schedule.id
            )
            db.add(calendar_event)
            db.commit()

        return missed_schedules

    async def reschedule_appointment(
        self,
        db: Session,
        schedule_id: int,
        new_date: datetime,
        reason: str,
        user_id: int
    ) -> Optional[Schedule]:
        """Reschedule an appointment."""
        schedule = await self.get_schedule(db, schedule_id)
        if not schedule:
            return None

        # Create override record
        override = ScheduleOverride(
            schedule_id=schedule_id,
            override_type="reschedule",
            reason=reason,
            new_date=new_date,
            created_by=user_id
        )
        db.add(override)

        # Update schedule
        schedule.original_date = schedule.scheduled_date
        schedule.scheduled_date = new_date
        schedule.status = ScheduleStatus.RESCHEDULED
        schedule.reschedule_count += 1
        schedule.reschedule_reason = reason
        schedule.rescheduled_by = user_id

        db.commit()
        db.refresh(schedule)

        # Update calendar event
        calendar_event = db.query(CalendarEvent).filter(
            CalendarEvent.schedule_id == schedule.id
        ).first()
        if calendar_event:
            calendar_event.start_time = new_date
            calendar_event.end_time = new_date + timedelta(hours=1)
            db.commit()

        return schedule

    async def import_moh_rules(self, db: Session, rules_data: List[Dict[str, Any]]) -> List[ScheduleRule]:
        """Import Ministry of Health immunization rules."""
        imported_rules = []
        for rule_data in rules_data:
            rule = ScheduleRule(
                name=rule_data["name"],
                schedule_type=ScheduleType.IMMUNIZATION,
                protocol=rule_data["protocol"],
                active=True
            )
            db.add(rule)
            imported_rules.append(rule)
        
        db.commit()
        for rule in imported_rules:
            db.refresh(rule)
        
        return imported_rules

    async def create_custom_rule(
        self,
        db: Session,
        name: str,
        schedule_type: ScheduleType,
        protocol: Dict[str, Any]
    ) -> ScheduleRule:
        """Create a custom scheduling rule."""
        rule = ScheduleRule(
            name=name,
            schedule_type=schedule_type,
            protocol=protocol,
            active=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

# Create a singleton instance
scheduling_service = SchedulingService() 