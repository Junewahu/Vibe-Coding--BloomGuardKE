from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..services.patient import patient_service, PatientService
from ..schemas.patient import (
    BiometricDataCreate, BiometricDataUpdate, BiometricDataResponse,
    PatientPhotoCreate, PatientPhotoUpdate, PatientPhotoResponse,
    BulkImportCreate, BulkImportUpdate, BulkImportResponse,
    ImportStats,
    PatientCreate, PatientUpdate, PatientResponse,
    CaregiverCreate, CaregiverUpdate, CaregiverResponse,
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse,
    ImmunizationCreate, ImmunizationUpdate, ImmunizationResponse,
    BulkImportResponse
)
from ..models.patient import BiometricType
from ..auth.dependencies import get_current_user
import logging

router = APIRouter(prefix="/patients", tags=["patients"])
logger = logging.getLogger(__name__)

# Biometric Data Endpoints
@router.post("/{patient_id}/biometric", response_model=BiometricDataResponse)
async def create_biometric_data(
    patient_id: int,
    biometric_data: BiometricDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new biometric data for a patient."""
    try:
        return await patient_service.create_biometric_data(
            db,
            patient_id,
            biometric_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/biometric/{biometric_id}", response_model=BiometricDataResponse)
async def update_biometric_data(
    biometric_id: int,
    biometric_data: BiometricDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update biometric data."""
    try:
        return await patient_service.update_biometric_data(
            db,
            biometric_id,
            biometric_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{patient_id}/biometric", response_model=List[BiometricDataResponse])
async def get_biometric_data(
    patient_id: int,
    biometric_type: Optional[BiometricType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get biometric data for a patient."""
    return await patient_service.get_biometric_data(
        db,
        patient_id,
        biometric_type=biometric_type
    )

# Patient Photo Endpoints
@router.post("/{patient_id}/photos", response_model=PatientPhotoResponse)
async def create_patient_photo(
    patient_id: int,
    photo: UploadFile = File(...),
    photo_type: str = Query(..., description="Type of photo (profile, id_card, etc.)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new photo for a patient."""
    try:
        photo_data = await photo.read()
        photo_create = PatientPhotoCreate(
            photo_type=photo_type,
            photo_data=photo_data
        )
        return await patient_service.create_patient_photo(
            db,
            patient_id,
            photo_create
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/photos/{photo_id}", response_model=PatientPhotoResponse)
async def update_patient_photo(
    photo_id: int,
    photo_data: PatientPhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update patient photo."""
    try:
        return await patient_service.update_patient_photo(
            db,
            photo_id,
            photo_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{patient_id}/photos", response_model=List[PatientPhotoResponse])
async def get_patient_photos(
    patient_id: int,
    photo_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get photos for a patient."""
    return await patient_service.get_patient_photos(
        db,
        patient_id,
        photo_type=photo_type
    )

# Bulk Import Endpoints
@router.post("/import", response_model=BulkImportResponse)
async def create_bulk_import(
    import_data: BulkImportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new bulk import record."""
    try:
        return await patient_service.create_bulk_import(
            db,
            import_data,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import/{import_id}/process")
async def process_bulk_import(
    import_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Process bulk import file."""
    try:
        file_data = await file.read()
        background_tasks.add_task(
            patient_service.process_bulk_import,
            db,
            import_id,
            file_data
        )
        return {"message": "Import processing started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/import/stats", response_model=ImportStats)
async def get_import_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bulk import statistics."""
    try:
        return await patient_service.get_import_stats(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new patient record"""
    try:
        patient_service = PatientService(db)
        return await patient_service.create_patient(patient_data)
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing patient record"""
    try:
        patient_service = PatientService(db)
        patient = await patient_service.update_patient(patient_id, patient_data)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get patient by ID"""
    try:
        patient_service = PatientService(db)
        patient = await patient_service.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of patients"""
    try:
        patient_service = PatientService(db)
        return await patient_service.get_patients(skip, limit)
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{patient_id}/medical-records", response_model=MedicalRecordResponse)
async def create_medical_record(
    patient_id: str,
    record_data: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new medical record for a patient"""
    try:
        patient_service = PatientService(db)
        return await patient_service.create_medical_record(record_data)
    except Exception as e:
        logger.error(f"Error creating medical record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{patient_id}/immunizations", response_model=ImmunizationResponse)
async def create_immunization(
    patient_id: str,
    immunization_data: ImmunizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new immunization record for a patient"""
    try:
        patient_service = PatientService(db)
        return await patient_service.create_immunization(immunization_data)
    except Exception as e:
        logger.error(f"Error creating immunization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_patients(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import patients from Excel file"""
    try:
        # Save file temporarily
        file_location = f"temp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        patient_service = PatientService(db)
        result = await patient_service.bulk_import_patients(
            file_location,
            current_user.id
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in bulk import: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_patient_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get patient statistics"""
    try:
        patient_service = PatientService(db)
        return await patient_service.get_patient_stats()
    except Exception as e:
        logger.error(f"Error getting patient stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query}")
async def search_patients(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search patients by name, phone, or NHIF number"""
    try:
        patient_service = PatientService(db)
        return await patient_service.search_patients(query, limit)
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 