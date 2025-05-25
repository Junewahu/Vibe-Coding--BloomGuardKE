from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
from .. import models, schemas

def get_medical_record(db: Session, record_id: int) -> Optional[models.MedicalRecord]:
    """Get a medical record by ID"""
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()

def get_medical_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None
) -> List[models.MedicalRecord]:
    """Get all medical records with optional filters"""
    query = db.query(models.MedicalRecord)
    if patient_id:
        query = query.filter(models.MedicalRecord.patient_id == patient_id)
    if doctor_id:
        query = query.filter(models.MedicalRecord.doctor_id == doctor_id)
    return query.offset(skip).limit(limit).all()

def create_medical_record(db: Session, record: schemas.MedicalRecordCreate) -> models.MedicalRecord:
    """Create a new medical record"""
    db_record = models.MedicalRecord(
        patient_id=record.patient_id,
        doctor_id=record.doctor_id,
        record_type=record.record_type,
        title=record.title,
        description=record.description,
        diagnosis=record.diagnosis,
        treatment=record.treatment,
        notes=record.notes,
        attachments=record.attachments,
        metadata=record.metadata,
        follow_up_required=record.follow_up_required,
        follow_up_date=record.follow_up_date
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def update_medical_record(
    db: Session,
    record_id: int,
    record: schemas.MedicalRecordUpdate
) -> Optional[models.MedicalRecord]:
    """Update a medical record"""
    db_record = get_medical_record(db, record_id)
    if not db_record:
        return None
    update_data = record.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_medical_record(db: Session, record_id: int) -> bool:
    """Delete a medical record"""
    db_record = get_medical_record(db, record_id)
    if not db_record:
        return False
    db.delete(db_record)
    db.commit()
    return True

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

def get_doctor_medical_records(
    db: Session,
    doctor_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get all medical records created by a doctor"""
    return db.query(models.MedicalRecord)\
        .filter(models.MedicalRecord.doctor_id == doctor_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_follow_up_required_records(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get all medical records that require follow-up"""
    today = date.today()
    return db.query(models.MedicalRecord)\
        .filter(
            models.MedicalRecord.follow_up_required == True,
            models.MedicalRecord.follow_up_date != None,
            models.MedicalRecord.follow_up_date <= today
        )\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_records_by_type(
    db: Session,
    record_type: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get medical records by type"""
    return db.query(models.MedicalRecord)\
        .filter(models.MedicalRecord.record_type == record_type)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_records_with_attachments(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get medical records that have attachments"""
    return db.query(models.MedicalRecord)\
        .filter(models.MedicalRecord.attachments != None)\
        .filter(models.MedicalRecord.attachments != [])\
        .offset(skip)\
        .limit(limit)\
        .all()

def add_attachment_to_record(
    db: Session,
    record_id: int,
    attachment: dict
) -> Optional[models.MedicalRecord]:
    """Add an attachment to a medical record"""
    db_record = get_medical_record(db, record_id)
    if not db_record:
        return None
    
    if not db_record.attachments:
        db_record.attachments = []
    
    db_record.attachments.append(attachment)
    db.commit()
    db.refresh(db_record)
    return db_record

def remove_attachment_from_record(
    db: Session,
    record_id: int,
    attachment_id: str
) -> Optional[models.MedicalRecord]:
    """Remove an attachment from a medical record"""
    db_record = get_medical_record(db, record_id)
    if not db_record or not db_record.attachments:
        return None
    
    db_record.attachments = [
        att for att in db_record.attachments
        if att.get("id") != attachment_id
    ]
    
    db.commit()
    db.refresh(db_record)
    return db_record

def get_records_by_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    skip: int = 0,
    limit: int = 100
) -> List[models.MedicalRecord]:
    """Get medical records within a date range"""
    return db.query(models.MedicalRecord)\
        .filter(
            and_(
                models.MedicalRecord.created_at >= start_date,
                models.MedicalRecord.created_at <= end_date
            )
        )\
        .offset(skip)\
        .limit(limit)\
        .all() 