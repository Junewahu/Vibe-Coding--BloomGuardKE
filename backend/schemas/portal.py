from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from enum import Enum
from ..models.portal import (
    MedicalRecordType, PrescriptionStatus,
    HealthMetricType, MessageType
)

class MedicalRecordBase(BaseModel):
    record_type: MedicalRecordType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MedicalRecordCreate(MedicalRecordBase):
    patient_id: int
    doctor_id: int

class MedicalRecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    patient_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PrescriptionBase(BaseModel):
    medication_name: str = Field(..., min_length=1, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    duration: str = Field(..., min_length=1, max_length=100)
    instructions: Optional[str] = None
    start_date: date
    end_date: date
    max_refills: int = Field(0, ge=0)
    notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    patient_id: int
    doctor_id: int

class PrescriptionUpdate(BaseModel):
    status: Optional[PrescriptionStatus] = None
    refill_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    id: int
    patient_id: int
    doctor_id: int
    status: PrescriptionStatus
    refill_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class HealthMetricBase(BaseModel):
    metric_type: HealthMetricType
    value: float
    unit: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = None
    recorded_at: datetime

class HealthMetricCreate(HealthMetricBase):
    patient_id: int

class HealthMetricUpdate(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

class HealthMetricResponse(HealthMetricBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PortalMessageBase(BaseModel):
    message_type: MessageType
    subject: str = Field(..., min_length=1, max_length=200)
    content: str
    attachments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class PortalMessageCreate(PortalMessageBase):
    patient_id: int
    sender_id: int

class PortalMessageUpdate(BaseModel):
    is_read: Optional[bool] = None

class PortalMessageResponse(PortalMessageBase):
    id: int
    patient_id: int
    sender_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PortalNotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str
    notification_type: str = Field(..., min_length=1, max_length=50)
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PortalNotificationCreate(PortalNotificationBase):
    patient_id: int

class PortalNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class PortalNotificationResponse(PortalNotificationBase):
    id: int
    patient_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PatientPortalStats(BaseModel):
    total_records: int
    active_prescriptions: int
    recent_health_metrics: List[HealthMetricResponse]
    unread_messages: int
    unread_notifications: int
    upcoming_appointments: int
    recent_records: List[MedicalRecordResponse]
    recent_prescriptions: List[PrescriptionResponse] 