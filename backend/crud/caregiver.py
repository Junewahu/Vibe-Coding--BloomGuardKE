from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import models, schemas

def get_caregiver(db: Session, caregiver_id: int) -> Optional[models.Caregiver]:
    """Get a caregiver by ID"""
    return db.query(models.Caregiver).filter(models.Caregiver.id == caregiver_id).first()

def get_caregivers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Caregiver]:
    """Get all caregivers with optional search"""
    query = db.query(models.Caregiver)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                models.Caregiver.first_name.ilike(search),
                models.Caregiver.last_name.ilike(search),
                models.Caregiver.phone_number.ilike(search),
                models.Caregiver.email.ilike(search)
            )
        )
    
    return query.offset(skip).limit(limit).all()

def create_caregiver(db: Session, caregiver: schemas.CaregiverCreate) -> models.Caregiver:
    """Create a new caregiver"""
    db_caregiver = models.Caregiver(
        first_name=caregiver.first_name,
        last_name=caregiver.last_name,
        phone_number=caregiver.phone_number,
        email=caregiver.email,
        address=caregiver.address,
        relationship=caregiver.relationship,
        notes=caregiver.notes
    )
    db.add(db_caregiver)
    db.commit()
    db.refresh(db_caregiver)
    return db_caregiver

def update_caregiver(
    db: Session,
    caregiver_id: int,
    caregiver: schemas.CaregiverUpdate
) -> Optional[models.Caregiver]:
    """Update a caregiver"""
    db_caregiver = get_caregiver(db, caregiver_id)
    if not db_caregiver:
        return None
    update_data = caregiver.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_caregiver, field, value)
    db.commit()
    db.refresh(db_caregiver)
    return db_caregiver

def delete_caregiver(db: Session, caregiver_id: int) -> bool:
    """Delete a caregiver"""
    db_caregiver = get_caregiver(db, caregiver_id)
    if not db_caregiver:
        return False
    db.delete(db_caregiver)
    db.commit()
    return True

def get_caregiver_patients(
    db: Session,
    caregiver_id: int
) -> List[models.Patient]:
    """Get all patients for a caregiver"""
    caregiver = get_caregiver(db, caregiver_id)
    if not caregiver:
        return []
    return caregiver.patients

def add_patient_to_caregiver(
    db: Session,
    caregiver_id: int,
    patient_id: int
) -> Optional[models.Caregiver]:
    """Add a patient to a caregiver"""
    caregiver = get_caregiver(db, caregiver_id)
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not caregiver or not patient:
        return None
    caregiver.patients.append(patient)
    db.commit()
    db.refresh(caregiver)
    return caregiver

def remove_patient_from_caregiver(
    db: Session,
    caregiver_id: int,
    patient_id: int
) -> Optional[models.Caregiver]:
    """Remove a patient from a caregiver"""
    caregiver = get_caregiver(db, caregiver_id)
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not caregiver or not patient:
        return None
    caregiver.patients.remove(patient)
    db.commit()
    db.refresh(caregiver)
    return caregiver

def get_caregiver_by_phone(
    db: Session,
    phone_number: str
) -> Optional[models.Caregiver]:
    """Get a caregiver by phone number"""
    return db.query(models.Caregiver)\
        .filter(models.Caregiver.phone_number == phone_number)\
        .first()

def get_caregiver_by_email(
    db: Session,
    email: str
) -> Optional[models.Caregiver]:
    """Get a caregiver by email"""
    return db.query(models.Caregiver)\
        .filter(models.Caregiver.email == email)\
        .first()

def get_caregivers_by_relationship(
    db: Session,
    relationship: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Caregiver]:
    """Get caregivers by relationship type"""
    return db.query(models.Caregiver)\
        .filter(models.Caregiver.relationship == relationship)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_caregivers_with_multiple_patients(
    db: Session,
    min_patients: int = 2,
    skip: int = 0,
    limit: int = 100
) -> List[models.Caregiver]:
    """Get caregivers with multiple patients"""
    return db.query(models.Caregiver)\
        .join(models.Caregiver.patients)\
        .group_by(models.Caregiver.id)\
        .having(db.func.count(models.Patient.id) >= min_patients)\
        .offset(skip)\
        .limit(limit)\
        .all() 