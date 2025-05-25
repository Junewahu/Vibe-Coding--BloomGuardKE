from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/", response_model=schemas.Reminder)
def create_reminder(
    reminder: schemas.ReminderCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Create a new reminder"""
    return crud.reminder.create_reminder(db=db, reminder=reminder)

@router.get("/", response_model=List[schemas.Reminder])
def read_reminders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all reminders with optional filters"""
    return crud.reminder.get_reminders(
        db,
        skip=skip,
        limit=limit,
        status=status,
        channel=channel,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{reminder_id}", response_model=schemas.Reminder)
def read_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get a specific reminder"""
    reminder = crud.reminder.get_reminder(db, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.put("/{reminder_id}", response_model=schemas.Reminder)
def update_reminder(
    reminder_id: int,
    reminder: schemas.ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Update a reminder"""
    updated_reminder = crud.reminder.update_reminder(db, reminder_id, reminder)
    if updated_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated_reminder

@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Delete a reminder"""
    success = crud.reminder.delete_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}

@router.get("/pending", response_model=List[schemas.Reminder])
def read_pending_reminders(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all pending reminders"""
    return crud.reminder.get_pending_reminders(db)

@router.get("/stats", response_model=dict)
def read_reminder_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get reminder statistics"""
    return crud.reminder.get_reminder_stats(db)

@router.post("/{reminder_id}/retry")
def retry_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Retry a failed reminder"""
    success = crud.reminder.retry_failed_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder scheduled for retry"} 