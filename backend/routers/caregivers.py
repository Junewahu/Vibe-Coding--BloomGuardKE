from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/caregivers", tags=["caregivers"])

@router.post("/", response_model=schemas.Caregiver)
def create_caregiver(
    caregiver: schemas.CaregiverCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Create a new caregiver"""
    return crud.caregiver.create_caregiver(db=db, caregiver=caregiver)

@router.get("/", response_model=List[schemas.Caregiver])
def read_caregivers(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all caregivers with optional filters"""
    return crud.caregiver.get_caregivers(
        db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        search=search
    )

@router.get("/{caregiver_id}", response_model=schemas.Caregiver)
def read_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get a specific caregiver"""
    caregiver = crud.caregiver.get_caregiver(db, caregiver_id)
    if caregiver is None:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return caregiver

@router.put("/{caregiver_id}", response_model=schemas.Caregiver)
def update_caregiver(
    caregiver_id: int,
    caregiver: schemas.CaregiverUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Update a caregiver"""
    updated_caregiver = crud.caregiver.update_caregiver(db, caregiver_id, caregiver)
    if updated_caregiver is None:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return updated_caregiver

@router.delete("/{caregiver_id}")
def delete_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Delete a caregiver"""
    success = crud.caregiver.delete_caregiver(db, caregiver_id)
    if not success:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return {"message": "Caregiver deleted successfully"}

@router.post("/{caregiver_id}/patients/{patient_id}")
def add_patient_to_caregiver(
    caregiver_id: int,
    patient_id: int,
    relationship: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Add a patient to a caregiver"""
    success = crud.caregiver.add_patient(
        db,
        caregiver_id=caregiver_id,
        patient_id=patient_id,
        relationship=relationship
    )
    if not success:
        raise HTTPException(status_code=404, detail="Caregiver or patient not found")
    return {"message": "Patient added to caregiver successfully"}

@router.delete("/{caregiver_id}/patients/{patient_id}")
def remove_patient_from_caregiver(
    caregiver_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Remove a patient from a caregiver"""
    success = crud.caregiver.remove_patient(db, caregiver_id, patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Caregiver or patient not found")
    return {"message": "Patient removed from caregiver successfully"}

@router.get("/{caregiver_id}/patients", response_model=List[schemas.Patient])
def get_caregiver_patients(
    caregiver_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get all patients for a caregiver"""
    patients = crud.caregiver.get_caregiver_patients(db, caregiver_id)
    if patients is None:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return patients

@router.get("/stats")
def get_caregiver_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """Get statistics for caregivers"""
    return crud.caregiver.get_caregiver_stats(db) 