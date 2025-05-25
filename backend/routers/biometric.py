from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any
import base64

from ..database import get_db
from ..services.biometric import biometric_service
from ..auth import get_current_active_user, check_admin_permission
from ..models.user import User
from ..schemas.biometric import BiometricRecordCreate, BiometricRecordResponse

router = APIRouter()

@router.post("/capture/fingerprint/{patient_id}", response_model=BiometricRecordResponse)
async def capture_fingerprint(
    patient_id: int,
    fingerprint_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Capture and store fingerprint data for a patient."""
    try:
        fingerprint_data = await fingerprint_file.read()
        biometric_record = biometric_service.capture_fingerprint(
            patient_id=patient_id,
            fingerprint_data=fingerprint_data,
            db=db
        )
        return biometric_record
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/capture/facial/{patient_id}", response_model=BiometricRecordResponse)
async def capture_facial_id(
    patient_id: int,
    facial_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Capture and store facial recognition data for a patient."""
    try:
        facial_data = await facial_file.read()
        biometric_record = biometric_service.capture_facial_id(
            patient_id=patient_id,
            facial_data=facial_data,
            db=db
        )
        return biometric_record
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/verify/{patient_id}", response_model=Dict[str, bool])
async def verify_biometric(
    patient_id: int,
    biometric_type: str,
    biometric_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify biometric data against stored records."""
    try:
        biometric_data = await biometric_file.read()
        is_valid = biometric_service.verify_biometric(
            patient_id=patient_id,
            biometric_type=biometric_type,
            biometric_data=biometric_data,
            db=db
        )
        return {"is_valid": is_valid}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/link/nhif/{patient_id}", response_model=BiometricRecordResponse)
async def link_nhif_biometric(
    patient_id: int,
    nhif_id: str,
    biometric_type: str,
    biometric_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Link NHIF ID with biometric data."""
    try:
        biometric_data = await biometric_file.read()
        biometric_record = biometric_service.link_nhif_biometric(
            patient_id=patient_id,
            nhif_id=nhif_id,
            biometric_type=biometric_type,
            biometric_data=biometric_data,
            db=db
        )
        return biometric_record
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/verify/nhif/{nhif_id}", response_model=Dict[str, Any])
async def verify_nhif_id(
    nhif_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Verify NHIF ID with the NHIF API."""
    try:
        nhif_data = biometric_service.verify_nhif_id(nhif_id)
        return nhif_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 