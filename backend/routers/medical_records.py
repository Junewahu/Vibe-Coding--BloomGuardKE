from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..crud import medical_record as medical_record_crud
from ..auth import get_current_active_user

router = APIRouter(prefix="/medical-records", tags=["medical-records"])

@router.post("/", response_model=schemas.MedicalRecord)
def create_medical_record(
    record: schemas.MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new medical record"""
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return medical_record_crud.create_medical_record(db=db, record=record)

@router.get("/", response_model=List[schemas.MedicalRecord])
def read_medical_records(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    record_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all medical records with optional filters"""
    return medical_record_crud.get_medical_records(
        db=db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        doctor_id=doctor_id,
        record_type=record_type,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{record_id}", response_model=schemas.MedicalRecord)
def read_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific medical record"""
    medical_record = medical_record_crud.get_medical_record(db=db, record_id=record_id)
    if medical_record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return medical_record

@router.put("/{record_id}", response_model=schemas.MedicalRecord)
def update_medical_record(
    record_id: int,
    record: schemas.MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update a medical record"""
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_record = medical_record_crud.update_medical_record(
        db=db, record_id=record_id, medical_record=medical_record
    )
    if updated_record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return updated_record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a medical record"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    success = medical_record_crud.delete_medical_record(db=db, record_id=record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return None

@router.get("/patient/{patient_id}", response_model=List[schemas.MedicalRecord])
def read_patient_medical_records(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    record_type: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all medical records for a specific patient"""
    return medical_record_crud.get_patient_medical_records(
        db=db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
        record_type=record_type
    )

@router.get("/doctor/{doctor_id}", response_model=List[schemas.MedicalRecord])
def read_doctor_medical_records(
    doctor_id: int,
    skip: int = 0,
    limit: int = 100,
    record_type: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all medical records created by a specific doctor"""
    return medical_record_crud.get_doctor_medical_records(
        db=db,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit,
        record_type=record_type
    )

@router.get("/follow-up/required", response_model=List[schemas.MedicalRecord])
def read_follow_up_required_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all medical records that require follow-up"""
    return medical_record_crud.get_follow_up_required_records(
        db=db, skip=skip, limit=limit
    ) 