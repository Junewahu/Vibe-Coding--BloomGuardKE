from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date
from .. import models, schemas
from ..auth import get_password_hash

def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    """Get a patient by ID"""
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Patient]:
    """Get all patients with optional search"""
    query = db.query(models.Patient)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                models.Patient.first_name.ilike(search),
                models.Patient.last_name.ilike(search),
                models.Patient.phone_number.ilike(search),
                models.Patient.email.ilike(search),
                models.Patient.nhif_number.ilike(search)
            )
        )
    
    return query.offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate) -> models.Patient:
    """Create a new patient"""
    db_patient = models.Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        phone_number=patient.phone_number,
        email=patient.email,
        address=patient.address,
        nhif_number=patient.nhif_number,
        blood_type=patient.blood_type,
        allergies=patient.allergies,
        chronic_conditions=patient.chronic_conditions,
        notes=patient.notes
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(
    db: Session,
    patient_id: int,
    patient: schemas.PatientUpdate
) -> Optional[models.Patient]:
    """Update a patient"""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int) -> bool:
    """Delete a patient"""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    
    db.delete(db_patient)
    db.commit()
    return True

def get_patient_appointments(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Appointment]:
    """Get all appointments for a patient"""
    return db.query(models.Appointment)\
        .filter(models.Appointment.patient_id == patient_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_patient_medical_records(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get all medical records for a patient"""
    return db.query(models.MedicalRecord)\
        .filter(models.MedicalRecord.patient_id == patient_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_patient_caregivers(
    db: Session,
    patient_id: int
) -> List[models.Caregiver]:
    """Get all caregivers for a patient"""
    patient = get_patient(db, patient_id)
    if not patient:
        return []
    return patient.caregivers

def bulk_create_patients(
    db: Session,
    patients: List[schemas.PatientCreate]
) -> List[models.Patient]:
    """Bulk create patients from a list"""
    db_patients = []
    for patient in patients:
        db_patient = create_patient(db, patient)
        db_patients.append(db_patient)
    return db_patients

def get_patients_by_age_range(
    db: Session,
    min_age: int,
    max_age: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Patient]:
    """Get patients within an age range"""
    today = date.today()
    min_date = date(today.year - max_age, today.month, today.day)
    max_date = date(today.year - min_age, today.month, today.day)
    
    return db.query(models.Patient)\
        .filter(models.Patient.date_of_birth.between(min_date, max_date))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_patients_by_last_visit(
    db: Session,
    days: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Patient]:
    """Get patients who haven't visited in X days"""
    from datetime import timedelta
    cutoff_date = date.today() - timedelta(days=days)
    
    return db.query(models.Patient)\
        .filter(
            or_(
                models.Patient.last_visit_date == None,
                models.Patient.last_visit_date < cutoff_date
            )
        )\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_patients_with_upcoming_appointments(
    db: Session,
    days: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Patient]:
    """Get patients with appointments in the next X days"""
    from datetime import timedelta
    today = date.today()
    future_date = today + timedelta(days=days)
    
    return db.query(models.Patient)\
        .join(models.Appointment)\
        .filter(
            models.Appointment.scheduled_at.between(today, future_date),
            models.Appointment.status == "scheduled"
        )\
        .distinct()\
        .offset(skip)\
        .limit(limit)\
        .all() 