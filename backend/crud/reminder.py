from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from .. import models, schemas

def get_reminder(db: Session, reminder_id: int) -> Optional[models.Reminder]:
    """Get a reminder by ID"""
    return db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()

def get_reminders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[models.Reminder]:
    """Get all reminders with optional filters"""
    query = db.query(models.Reminder)
    if status:
        query = query.filter(models.Reminder.status == status)
    if channel:
        query = query.filter(models.Reminder.channel == channel)
    if start_date:
        query = query.filter(models.Reminder.scheduled_at >= start_date)
    if end_date:
        query = query.filter(models.Reminder.scheduled_at <= end_date)
    return query.offset(skip).limit(limit).all()

def create_reminder(db: Session, reminder: schemas.ReminderCreate) -> models.Reminder:
    """Create a new reminder"""
    db_reminder = models.Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def update_reminder(
    db: Session,
    reminder_id: int,
    reminder: schemas.ReminderUpdate
) -> Optional[models.Reminder]:
    """Update a reminder"""
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return None
    update_data = reminder.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reminder, field, value)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: int) -> bool:
    """Delete a reminder"""
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return False
    db.delete(db_reminder)
    db.commit()
    return True

def get_pending_reminders(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.Reminder]:
    """Get all pending reminders"""
    return db.query(models.Reminder)\
        .filter(models.Reminder.status == "pending")\
        .offset(skip)\
        .limit(limit)\
        .all()

def mark_reminder_sent(
    db: Session,
    reminder_id: int,
    sent_at: Optional[datetime] = None
) -> Optional[models.Reminder]:
    """Mark a reminder as sent"""
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return None
    
    db_reminder.status = "sent"
    db_reminder.sent_at = sent_at or datetime.now()
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def mark_reminder_failed(
    db: Session,
    reminder_id: int,
    error_message: str
) -> Optional[models.Reminder]:
    """Mark a reminder as failed"""
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return None
    
    db_reminder.status = "failed"
    db_reminder.error_message = error_message
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminder_stats(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    """Get statistics for reminders"""
    query = db.query(models.Reminder)
    if start_date:
        query = query.filter(models.Reminder.scheduled_at >= start_date)
    if end_date:
        query = query.filter(models.Reminder.scheduled_at <= end_date)
    total = query.count()
    sent = query.filter(models.Reminder.status == "sent").count()
    failed = query.filter(models.Reminder.status == "failed").count()
    pending = query.filter(models.Reminder.status == "pending").count()
    return {"total": total, "sent": sent, "failed": failed, "pending": pending}

def get_upcoming_reminders(
    db: Session,
    hours: int = 24,
    skip: int = 0,
    limit: int = 100
) -> List[models.Reminder]:
    """Get reminders scheduled within the next X hours"""
    now = datetime.now()
    future = now + timedelta(hours=hours)
    
    return db.query(models.Reminder)\
        .filter(
            and_(
                models.Reminder.scheduled_at.between(now, future),
                models.Reminder.status == "pending"
            )
        )\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_failed_reminders(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.Reminder]:
    """Get all failed reminders"""
    return db.query(models.Reminder)\
        .filter(models.Reminder.status == "failed")\
        .offset(skip)\
        .limit(limit)\
        .all()

def retry_failed_reminder(
    db: Session,
    reminder_id: int,
    new_scheduled_at: Optional[datetime] = None
) -> Optional[models.Reminder]:
    """Retry a failed reminder"""
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder or db_reminder.status != "failed":
        return None
    
    db_reminder.status = "pending"
    if new_scheduled_at:
        db_reminder.scheduled_at = new_scheduled_at
    db_reminder.error_message = None
    db_reminder.retry_count = (db_reminder.retry_count or 0) + 1
    
    db.commit()
    db.refresh(db_reminder)
    return db_reminder 