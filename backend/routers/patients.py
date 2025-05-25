from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
import pandas as pd
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas, auth
from ..database import get_db
from ..models.patient import Patient, PatientAuditLog, DigitalConsent
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=schemas.Patient)
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Create a new patient"""
    return crud.patient.create_patient(db=db, patient=patient)

@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all patients with optional search"""
    return crud.patient.get_patients(db, skip=skip, limit=limit, search=search)

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get a specific patient"""
    patient = crud.patient.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int,
    patient: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Update a patient"""
    updated_patient = crud.patient.update_patient(db, patient_id, patient)
    if updated_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Delete a patient"""
    success = crud.patient.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

@router.get("/{patient_id}/appointments", response_model=List[schemas.Appointment])
def read_patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all appointments for a patient"""
    return crud.patient.get_patient_appointments(db, patient_id)

@router.get("/{patient_id}/medical-records", response_model=List[schemas.MedicalRecord])
def read_patient_medical_records(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all medical records for a patient"""
    return crud.patient.get_patient_medical_records(db, patient_id)

@router.get("/{patient_id}/caregivers", response_model=List[schemas.Caregiver])
def read_patient_caregivers(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all caregivers for a patient"""
    return crud.patient.get_patient_caregivers(db, patient_id)

@router.get("/age-range/{min_age}/{max_age}", response_model=List[schemas.Patient])
def read_patients_by_age_range(
    min_age: int,
    max_age: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get patients within an age range"""
    return crud.patient.get_patients_by_age_range(db, min_age, max_age)

@router.get("/last-visit/{days}", response_model=List[schemas.Patient])
def read_patients_by_last_visit(
    days: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get patients who haven't visited in specified days"""
    return crud.patient.get_patients_by_last_visit(db, days)

@router.get("/upcoming-appointments/{days}", response_model=List[schemas.Patient])
def read_patients_with_upcoming_appointments(
    days: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get patients with upcoming appointments"""
    return crud.patient.get_patients_with_upcoming_appointments(db, days)

@router.post("/import", summary="Bulk import patients from Excel/CSV/EMR")
def bulk_import_patients(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Bulk import patients from Excel/CSV/EMR. Flags incomplete/outdated records and logs audit."""
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .csv files are supported.")
    try:
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing error: {str(e)}")

    required_fields = ["first_name", "last_name", "date_of_birth", "gender"]
    results = []
    for idx, row in df.iterrows():
        patient_data = row.to_dict()
        missing_fields = [f for f in required_fields if not patient_data.get(f)]
        is_incomplete = len(missing_fields) > 0
        is_outdated = False
        last_verified_at = datetime.utcnow()
        # Check for outdated (e.g., last visit > 1 year ago)
        last_visit = patient_data.get("last_visit_date")
        if last_visit:
            try:
                last_visit_dt = pd.to_datetime(last_visit)
                if (datetime.utcnow() - last_visit_dt).days > 365:
                    is_outdated = True
            except Exception:
                is_outdated = True
        # Upsert patient (by unique fields, e.g., nhif_number or name+dob)
        nhif_number = patient_data.get("nhif_number")
        patient = None
        if nhif_number:
            patient = db.query(Patient).filter(Patient.nhif_number == nhif_number).first()
        if not patient:
            patient = db.query(Patient).filter(
                Patient.first_name == patient_data.get("first_name"),
                Patient.last_name == patient_data.get("last_name"),
                Patient.date_of_birth == pd.to_datetime(patient_data.get("date_of_birth")),
            ).first()
        if patient:
            # Update
            for key, value in patient_data.items():
                if hasattr(patient, key) and value is not None:
                    setattr(patient, key, value)
            patient.is_incomplete = is_incomplete
            patient.is_outdated = is_outdated
            patient.last_verified_at = last_verified_at
            action = "update"
        else:
            # Create
            patient = Patient(
                **{k: v for k, v in patient_data.items() if hasattr(Patient, k)},
                is_incomplete=is_incomplete,
                is_outdated=is_outdated,
                last_verified_at=last_verified_at
            )
            db.add(patient)
            action = "create"
        db.commit()
        db.refresh(patient)
        # Audit log
        audit = PatientAuditLog(
            patient_id=patient.id,
            action=action,
            performed_by=current_user.email,
            timestamp=datetime.utcnow(),
            changes=patient_data,
            ip_address=None,
            user_agent=None
        )
        db.add(audit)
        db.commit()
        results.append({
            "row": idx+1,
            "patient_id": patient.id,
            "action": action,
            "is_incomplete": is_incomplete,
            "is_outdated": is_outdated,
            "missing_fields": missing_fields
        })
    return {"imported": len(results), "results": results}

@router.post("/{patient_id}/consent", summary="Capture digital consent for a patient")
def capture_digital_consent(
    patient_id: int,
    consent_text: str = Body(..., embed=True),
    consent_given: bool = Body(..., embed=True),
    method: str = Body("digital", embed=True),
    metadata: Optional[dict] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Capture digital consent for a patient."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    consent = DigitalConsent(
        patient_id=patient_id,
        consent_text=consent_text,
        consent_given=consent_given,
        consented_by=current_user.email,
        method=method,
        metadata=metadata or {},
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    patient.consent_id = consent.id
    db.commit()
    return {"message": "Consent captured", "consent_id": consent.id}

@router.get("/{patient_id}/audit-logs", summary="Get audit logs for a patient")
def get_patient_audit_logs(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Retrieve audit logs for a patient."""
    logs = db.query(PatientAuditLog).filter(PatientAuditLog.patient_id == patient_id).order_by(PatientAuditLog.timestamp.desc()).all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "performed_by": log.performed_by,
            "timestamp": log.timestamp,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent
        }
        for log in logs
    ] 