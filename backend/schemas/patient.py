from pydantic import BaseModel, Field, EmailStr, constr, HttpUrl
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from .base import BaseSchema
from ..models.patient import BiometricType, Gender, PatientStatus

class CaregiverBase(BaseModel):
    first_name: str
    last_name: str
    relationship: str
    phone_number: str
    alternative_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: str
    county: str
    sub_county: str

class CaregiverCreate(CaregiverBase):
    pass

class CaregiverUpdate(CaregiverBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    relationship: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None

class CaregiverResponse(CaregiverBase):
    id: str
    registration_date: datetime
    last_updated: datetime
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class PatientBase(BaseModel):
    nhif_number: Optional[str] = None
    biometric_id: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    nationality: str
    language_preference: str
    phone_number: str
    alternative_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: str
    county: str
    sub_county: str
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    medical_history: Optional[Dict[str, Any]] = None

class PatientCreate(PatientBase):
    primary_caregiver: Optional[CaregiverCreate] = None

class PatientUpdate(BaseModel):
    nhif_number: Optional[str] = None
    biometric_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    nationality: Optional[str] = None
    language_preference: Optional[str] = None
    phone_number: Optional[str] = None
    alternative_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    medical_history: Optional[Dict[str, Any]] = None
    status: Optional[PatientStatus] = None
    primary_caregiver_id: Optional[str] = None

class PatientResponse(PatientBase):
    id: str
    status: PatientStatus
    registration_date: datetime
    last_updated: datetime
    is_complete: bool
    metadata: Optional[Dict[str, Any]] = None
    primary_caregiver: Optional[CaregiverResponse] = None

    class Config:
        orm_mode = True

class MedicalRecordBase(BaseModel):
    record_type: str
    record_date: datetime
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[HttpUrl]] = None

class MedicalRecordCreate(MedicalRecordBase):
    patient_id: str

class MedicalRecordUpdate(BaseModel):
    record_type: Optional[str] = None
    record_date: Optional[datetime] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[HttpUrl]] = None

class MedicalRecordResponse(MedicalRecordBase):
    id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ImmunizationBase(BaseModel):
    vaccine_name: str
    scheduled_date: datetime
    administered_date: Optional[datetime] = None
    batch_number: Optional[str] = None
    administered_by: Optional[str] = None
    status: str
    certificate_url: Optional[HttpUrl] = None

class ImmunizationCreate(ImmunizationBase):
    patient_id: str

class ImmunizationUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    administered_date: Optional[datetime] = None
    batch_number: Optional[str] = None
    administered_by: Optional[str] = None
    status: Optional[str] = None
    certificate_url: Optional[HttpUrl] = None

class ImmunizationResponse(ImmunizationBase):
    id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class BulkImportBase(BaseModel):
    file_url: HttpUrl
    import_type: str
    status: str
    total_records: int
    processed_records: int
    failed_records: int
    error_log: Optional[List[Dict[str, Any]]] = None

class BulkImportCreate(BulkImportBase):
    creator_id: str

class BulkImportUpdate(BaseModel):
    status: Optional[str] = None
    processed_records: Optional[int] = None
    failed_records: Optional[int] = None
    error_log: Optional[List[Dict[str, Any]]] = None

class BulkImportResponse(BulkImportBase):
    id: str
    created_at: datetime
    updated_at: datetime
    creator_id: str

    class Config:
        orm_mode = True

# Biometric schemas
class BiometricDataBase(BaseModel):
    biometric_type: BiometricType
    nhif_id: Optional[str] = None
    is_verified: bool = False

class BiometricDataCreate(BiometricDataBase):
    data: bytes  # Encrypted biometric data

class BiometricDataUpdate(BaseModel):
    nhif_id: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None

class BiometricDataResponse(BiometricDataBase):
    id: int
    patient_id: int
    capture_date: datetime
    verification_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Patient Photo schemas
class PatientPhotoBase(BaseModel):
    photo_type: str
    is_approved: bool = False

class PatientPhotoCreate(PatientPhotoBase):
    photo_data: bytes  # Encrypted photo data

class PatientPhotoUpdate(BaseModel):
    is_approved: Optional[bool] = None
    approval_date: Optional[datetime] = None

class PatientPhotoResponse(PatientPhotoBase):
    id: int
    patient_id: int
    capture_date: datetime
    approval_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Import Statistics schema
class ImportStats(BaseModel):
    total_imports: int
    successful_imports: int
    failed_imports: int
    average_success_rate: float
    imports_by_type: Dict[str, int]
    recent_imports: List[BulkImportResponse] 