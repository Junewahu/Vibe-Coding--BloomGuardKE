from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from .base import BaseSchema
from .patient import Patient
from .user import User

class MedicalRecordBase(BaseModel):
    """Base medical record schema with common fields"""
    patient_id: int
    doctor_id: int
    record_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    diagnosis: Optional[str] = Field(None, max_length=500)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    attachments: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None

class MedicalRecordCreate(MedicalRecordBase):
    """Schema for creating a new medical record"""
    pass

class MedicalRecordUpdate(BaseModel):
    """Schema for updating an existing medical record"""
    doctor_id: Optional[int] = None
    record_type: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    diagnosis: Optional[str] = Field(None, max_length=500)
    treatment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    attachments: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None

class MedicalRecordInDB(MedicalRecordBase, BaseSchema):
    """Schema for medical record data in database"""
    pass

class MedicalRecord(MedicalRecordInDB):
    """Schema for medical record response"""
    patient: Patient
    doctor: User
    is_follow_up_due: bool
    
    class Config:
        from_attributes = True 