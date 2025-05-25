from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from ..models.follow_up import FollowUpSchedule, FollowUpStatus
from ..models.appointment import Appointment, AppointmentStatus
from ..schemas.follow_up import FollowUpCreate, FollowUpUpdate
from ..services.notification import notification_service

class FollowUpService:
    def create_follow_up(
        self,
        db: Session,
        follow_up: FollowUpCreate
    ) -> FollowUpSchedule:
        """Create a new follow-up schedule with conflict checking."""
        # Check for conflicts
        is_available, conflicts = self.check_availability(
            db=db,
            doctor_id=follow_up.doctor_id,
            start_time=follow_up.scheduled_date,
            duration_minutes=follow_up.duration_minutes
        )
        
        if not is_available:
            raise ValueError(f"Time slot conflicts with existing schedules: {conflicts}")
        
        db_follow_up = FollowUpSchedule(**follow_up.dict())
        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up

    def get_follow_up(
        self,
        db: Session,
        follow_up_id: int
    ) -> Optional[FollowUpSchedule]:
        """Get a follow-up schedule by ID."""
        return db.query(FollowUpSchedule).filter(FollowUpSchedule.id == follow_up_id).first()

    def get_patient_follow_ups(
        self,
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FollowUpSchedule]:
        """Get all follow-ups for a patient."""
        return db.query(FollowUpSchedule)\
            .filter(FollowUpSchedule.patient_id == patient_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_doctor_follow_ups(
        self,
        db: Session,
        doctor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FollowUpSchedule]:
        """Get all follow-ups for a doctor."""
        return db.query(FollowUpSchedule)\
            .filter(FollowUpSchedule.doctor_id == doctor_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def update_follow_up(
        self,
        db: Session,
        follow_up_id: int,
        follow_up: FollowUpUpdate
    ) -> Optional[FollowUpSchedule]:
        """Update a follow-up schedule with conflict checking."""
        db_follow_up = self.get_follow_up(db, follow_up_id)
        if not db_follow_up:
            return None

        update_data = follow_up.dict(exclude_unset=True)
        
        # Check for conflicts if time is being updated
        if "scheduled_date" in update_data or "duration_minutes" in update_data:
            start_time = update_data.get("scheduled_date", db_follow_up.scheduled_date)
            duration = update_data.get("duration_minutes", db_follow_up.duration_minutes)
            
            is_available, conflicts = self.check_availability(
                db=db,
                doctor_id=db_follow_up.doctor_id,
                start_time=start_time,
                duration_minutes=duration,
                exclude_follow_up_id=follow_up_id
            )
            
            if not is_available:
                raise ValueError(f"Time slot conflicts with existing schedules: {conflicts}")

        for field, value in update_data.items():
            setattr(db_follow_up, field, value)

        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up

    def delete_follow_up(
        self,
        db: Session,
        follow_up_id: int
    ) -> bool:
        """Delete a follow-up schedule."""
        db_follow_up = self.get_follow_up(db, follow_up_id)
        if not db_follow_up:
            return False

        db.delete(db_follow_up)
        db.commit()
        return True

    def get_upcoming_follow_ups(
        self,
        db: Session,
        days: int = 7
    ) -> List[FollowUpSchedule]:
        """Get all upcoming follow-ups within the specified number of days."""
        end_date = datetime.utcnow() + timedelta(days=days)
        return db.query(FollowUpSchedule)\
            .filter(
                and_(
                    FollowUpSchedule.scheduled_date >= datetime.utcnow(),
                    FollowUpSchedule.scheduled_date <= end_date,
                    FollowUpSchedule.status == FollowUpStatus.SCHEDULED
                )
            )\
            .all()

    def send_follow_up_reminders(
        self,
        db: Session,
        days_before: int = 1
    ) -> List[Dict[str, Any]]:
        """Send reminders for upcoming follow-ups."""
        reminder_date = datetime.utcnow() + timedelta(days=days_before)
        follow_ups = db.query(FollowUpSchedule)\
            .filter(
                and_(
                    FollowUpSchedule.scheduled_date.date() == reminder_date.date(),
                    FollowUpSchedule.status == FollowUpStatus.SCHEDULED,
                    FollowUpSchedule.reminder_sent == False
                )
            )\
            .all()

        results = []
        for follow_up in follow_ups:
            try:
                # Send notification
                notification_service.send_follow_up_reminder(
                    patient_id=follow_up.patient_id,
                    follow_up_id=follow_up.id,
                    scheduled_date=follow_up.scheduled_date
                )
                
                # Update reminder status
                follow_up.reminder_sent = True
                db.commit()
                
                results.append({
                    "follow_up_id": follow_up.id,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "follow_up_id": follow_up.id,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def check_availability(
        self,
        db: Session,
        doctor_id: int,
        start_time: datetime,
        duration_minutes: int,
        exclude_follow_up_id: Optional[int] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check if a time slot is available for a follow-up."""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for conflicts with other follow-ups
        follow_up_query = db.query(FollowUpSchedule).filter(
            and_(
                FollowUpSchedule.doctor_id == doctor_id,
                FollowUpSchedule.status == FollowUpStatus.SCHEDULED,
                or_(
                    and_(
                        FollowUpSchedule.scheduled_date <= start_time,
                        FollowUpSchedule.scheduled_date + func.interval(f"{FollowUpSchedule.duration_minutes} minutes") > start_time
                    ),
                    and_(
                        FollowUpSchedule.scheduled_date < end_time,
                        FollowUpSchedule.scheduled_date + func.interval(f"{FollowUpSchedule.duration_minutes} minutes") >= end_time
                    )
                )
            )
        )
        
        if exclude_follow_up_id:
            follow_up_query = follow_up_query.filter(FollowUpSchedule.id != exclude_follow_up_id)
        
        follow_up_conflicts = follow_up_query.all()
        
        # Check for conflicts with appointments
        appointment_conflicts = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status == AppointmentStatus.SCHEDULED,
                or_(
                    and_(
                        Appointment.start_time <= start_time,
                        Appointment.end_time > start_time
                    ),
                    and_(
                        Appointment.start_time < end_time,
                        Appointment.end_time >= end_time
                    )
                )
            )
        ).all()
        
        conflicts = []
        for follow_up in follow_up_conflicts:
            conflicts.append({
                "type": "follow_up",
                "id": follow_up.id,
                "start_time": follow_up.scheduled_date,
                "end_time": follow_up.scheduled_date + timedelta(minutes=follow_up.duration_minutes)
            })
        
        for appointment in appointment_conflicts:
            conflicts.append({
                "type": "appointment",
                "id": appointment.id,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time
            })
        
        return len(conflicts) == 0, conflicts

    def find_available_slots(
        self,
        db: Session,
        doctor_id: int,
        date: datetime,
        duration_minutes: int,
        start_hour: int = 9,
        end_hour: int = 17
    ) -> List[Dict[str, datetime]]:
        """Find available time slots for a given date."""
        available_slots = []
        current_time = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            is_available, _ = self.check_availability(
                db=db,
                doctor_id=doctor_id,
                start_time=current_time,
                duration_minutes=duration_minutes
            )
            
            if is_available:
                available_slots.append({
                    "start_time": current_time,
                    "end_time": current_time + timedelta(minutes=duration_minutes)
                })
            
            current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return available_slots

    def convert_to_appointment(
        self,
        db: Session,
        follow_up_id: int
    ) -> Optional[Appointment]:
        """Convert a follow-up schedule to an appointment."""
        follow_up = self.get_follow_up(db, follow_up_id)
        if not follow_up:
            return None
        
        # Create appointment from follow-up
        appointment = Appointment(
            patient_id=follow_up.patient_id,
            doctor_id=follow_up.doctor_id,
            start_time=follow_up.scheduled_date,
            end_time=follow_up.scheduled_date + timedelta(minutes=follow_up.duration_minutes),
            status=AppointmentStatus.SCHEDULED,
            follow_up_id=follow_up_id,
            notes=f"Converted from follow-up: {follow_up.notes}" if follow_up.notes else None
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # Update follow-up status
        follow_up.status = FollowUpStatus.COMPLETED
        db.commit()
        
        return appointment

# Create singleton instance
follow_up_service = FollowUpService() 