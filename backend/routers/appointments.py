from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=schemas.Appointment)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Create a new appointment"""
    return crud.appointment.create_appointment(db=db, appointment=appointment)

@router.get("/", response_model=List[schemas.Appointment])
def read_appointments(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all appointments with optional filters"""
    return crud.appointment.get_appointments(
        db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=status
    )

@router.get("/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get a specific appointment"""
    appointment = crud.appointment.get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Update an appointment"""
    updated_appointment = crud.appointment.update_appointment(db, appointment_id, appointment)
    if updated_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Delete an appointment"""
    success = crud.appointment.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}

@router.get("/{appointment_id}/reminders", response_model=List[schemas.Reminder])
def read_appointment_reminders(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all reminders for an appointment"""
    return crud.appointment.get_appointment_reminders(db, appointment_id)

@router.get("/doctor/{doctor_id}/schedule/{date}", response_model=List[schemas.Appointment])
def read_doctor_schedule(
    doctor_id: int,
    date: datetime,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get a doctor's schedule for a specific date"""
    return crud.appointment.get_doctor_schedule(db, doctor_id, date)

@router.get("/upcoming/{days}", response_model=List[schemas.Appointment])
def read_upcoming_appointments(
    days: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all upcoming appointments in the next specified days"""
    return crud.appointment.get_upcoming_appointments(db, days) 