from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from .. import models, schemas

def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    """Get an appointment by ID"""
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[models.Appointment]:
    """Get all appointments with optional filters"""
    query = db.query(models.Appointment)
    if start_date:
        query = query.filter(models.Appointment.scheduled_at >= start_date)
    if end_date:
        query = query.filter(models.Appointment.scheduled_at <= end_date)
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(models.Appointment.patient_id == patient_id)
    if status:
        query = query.filter(models.Appointment.status == status)
    return query.offset(skip).limit(limit).all()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate) -> models.Appointment:
    """Create a new appointment"""
    db_appointment = models.Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        scheduled_at=appointment.scheduled_at,
        status=appointment.status,
        reason=appointment.reason,
        notes=appointment.notes,
        metadata=appointment.metadata
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(
    db: Session,
    appointment_id: int,
    appointment: schemas.AppointmentUpdate
) -> Optional[models.Appointment]:
    """Update an appointment"""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    update_data = appointment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int) -> bool:
    """Delete an appointment"""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return False
    db.delete(db_appointment)
    db.commit()
    return True

def get_appointment_reminders(
    db: Session,
    appointment_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Reminder]:
    """Get all reminders for an appointment"""
    return db.query(models.Reminder)\
        .filter(models.Reminder.appointment_id == appointment_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_appointment_reminder(
    db: Session,
    appointment_id: int,
    reminder: schemas.ReminderCreate
) -> models.Reminder:
    """Create a reminder for an appointment"""
    db_reminder = models.Reminder(
        appointment_id=appointment_id,
        **reminder.dict()
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_doctor_schedule(
    db: Session,
    doctor_id: int,
    date_: date
) -> List[models.Appointment]:
    """Get a doctor's schedule for a specific date"""
    start = datetime.combine(date_, datetime.min.time())
    end = datetime.combine(date_, datetime.max.time())
    return db.query(models.Appointment)\
        .filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.scheduled_at >= start,
            models.Appointment.scheduled_at <= end
        )\
        .all()

def get_upcoming_appointments(
    db: Session,
    days: int = 7,
    skip: int = 0,
    limit: int = 100
) -> List[models.Appointment]:
    """Get all upcoming appointments in the next X days"""
    now = datetime.now()
    future = now + timedelta(days=days)
    return db.query(models.Appointment)\
        .filter(
            models.Appointment.scheduled_at >= now,
            models.Appointment.scheduled_at <= future,
            models.Appointment.status == "scheduled"
        )\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_conflicting_appointments(
    db: Session,
    doctor_id: int,
    start_time: datetime,
    duration_minutes: int,
    exclude_appointment_id: Optional[int] = None
) -> List[models.Appointment]:
    """Get appointments that conflict with a given time slot"""
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    query = db.query(models.Appointment).filter(
        and_(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.status == "scheduled",
            or_(
                and_(
                    models.Appointment.scheduled_at <= start_time,
                    models.Appointment.scheduled_at + timedelta(minutes=models.Appointment.duration_minutes) > start_time
                ),
                and_(
                    models.Appointment.scheduled_at < end_time,
                    models.Appointment.scheduled_at + timedelta(minutes=models.Appointment.duration_minutes) >= end_time
                )
            )
        )
    )
    
    if exclude_appointment_id:
        query = query.filter(models.Appointment.id != exclude_appointment_id)
    
    return query.all()

def reschedule_appointment(
    db: Session,
    appointment_id: int,
    new_time: datetime,
    new_duration_minutes: Optional[int] = None
) -> Optional[models.Appointment]:
    """Reschedule an appointment to a new time"""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    # Check for conflicts
    duration = new_duration_minutes or db_appointment.duration_minutes
    conflicts = get_conflicting_appointments(
        db,
        db_appointment.doctor_id,
        new_time,
        duration,
        appointment_id
    )
    
    if conflicts:
        return None
    
    db_appointment.scheduled_at = new_time
    if new_duration_minutes:
        db_appointment.duration_minutes = new_duration_minutes
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment 