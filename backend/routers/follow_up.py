from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.follow_up import follow_up_service
from ..schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from ..auth import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=FollowUpResponse)
async def create_follow_up(
    follow_up: FollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new follow-up schedule."""
    try:
        return follow_up_service.create_follow_up(db, follow_up)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{follow_up_id}", response_model=FollowUpResponse)
async def get_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a follow-up schedule by ID."""
    follow_up = follow_up_service.get_follow_up(db, follow_up_id)
    if not follow_up:
        raise HTTPException(
            status_code=404,
            detail="Follow-up schedule not found"
        )
    return follow_up

@router.get("/patient/{patient_id}", response_model=List[FollowUpResponse])
async def get_patient_follow_ups(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all follow-ups for a patient."""
    return follow_up_service.get_patient_follow_ups(db, patient_id, skip, limit)

@router.get("/doctor/{doctor_id}", response_model=List[FollowUpResponse])
async def get_doctor_follow_ups(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all follow-ups for a doctor."""
    return follow_up_service.get_doctor_follow_ups(db, doctor_id, skip, limit)

@router.put("/{follow_up_id}", response_model=FollowUpResponse)
async def update_follow_up(
    follow_up_id: int,
    follow_up: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a follow-up schedule."""
    updated_follow_up = follow_up_service.update_follow_up(db, follow_up_id, follow_up)
    if not updated_follow_up:
        raise HTTPException(
            status_code=404,
            detail="Follow-up schedule not found"
        )
    return updated_follow_up

@router.delete("/{follow_up_id}")
async def delete_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a follow-up schedule."""
    success = follow_up_service.delete_follow_up(db, follow_up_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Follow-up schedule not found"
        )
    return {"message": "Follow-up schedule deleted successfully"}

@router.get("/upcoming/", response_model=List[FollowUpResponse])
async def get_upcoming_follow_ups(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all upcoming follow-ups within the specified number of days."""
    return follow_up_service.get_upcoming_follow_ups(db, days)

@router.post("/reminders/send")
async def send_follow_up_reminders(
    days_before: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send reminders for upcoming follow-ups."""
    results = follow_up_service.send_follow_up_reminders(db, days_before)
    return {
        "message": "Reminder sending process completed",
        "results": results
    }

@router.get("/availability/check")
async def check_availability(
    doctor_id: int,
    start_time: datetime,
    duration_minutes: int = Query(30, ge=15, le=180),
    exclude_follow_up_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if a time slot is available for a follow-up."""
    is_available, conflicts = follow_up_service.check_availability(
        db=db,
        doctor_id=doctor_id,
        start_time=start_time,
        duration_minutes=duration_minutes,
        exclude_follow_up_id=exclude_follow_up_id
    )
    return {
        "is_available": is_available,
        "conflicts": conflicts
    }

@router.get("/availability/slots")
async def find_available_slots(
    doctor_id: int,
    date: datetime,
    duration_minutes: int = Query(30, ge=15, le=180),
    start_hour: int = Query(9, ge=0, le=23),
    end_hour: int = Query(17, ge=0, le=23),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Find available time slots for a given date."""
    if start_hour >= end_hour:
        raise HTTPException(
            status_code=400,
            detail="Start hour must be before end hour"
        )
    
    slots = follow_up_service.find_available_slots(
        db=db,
        doctor_id=doctor_id,
        date=date,
        duration_minutes=duration_minutes,
        start_hour=start_hour,
        end_hour=end_hour
    )
    return {"available_slots": slots}

@router.post("/{follow_up_id}/convert-to-appointment")
async def convert_to_appointment(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Convert a follow-up schedule to an appointment."""
    appointment = follow_up_service.convert_to_appointment(db, follow_up_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Follow-up schedule not found"
        )
    return {
        "message": "Follow-up successfully converted to appointment",
        "appointment_id": appointment.id
    } 