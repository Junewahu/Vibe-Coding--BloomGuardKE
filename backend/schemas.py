from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import UserRole, ReminderChannel, ReminderStatus, AppointmentStatus

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Patient schemas
class PatientBase(BaseSchema):
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    phone_number: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    nhif_number: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    nhif_number: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_visit_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Caregiver schemas
class CaregiverBase(BaseSchema):
    first_name: str
    last_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    relationship: str
    notes: Optional[str] = None

class CaregiverCreate(CaregiverBase):
    pass

class CaregiverUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    relationship: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Caregiver(CaregiverBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Appointment schemas
class AppointmentBase(BaseSchema):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = 30
    appointment_type: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseSchema):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    appointment_type: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Appointment(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Reminder schemas
class ReminderBase(BaseSchema):
    appointment_id: int
    channel: ReminderChannel
    message: str
    scheduled_at: datetime
    status: ReminderStatus = ReminderStatus.PENDING

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseSchema):
    channel: Optional[ReminderChannel] = None
    message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[ReminderStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class Reminder(ReminderBase):
    id: int
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Medical Record schemas
class MedicalRecordBase(BaseSchema):
    patient_id: int
    doctor_id: int
    record_type: str
    title: str
    description: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None

class MedicalRecordCreate(MedicalRecordBase):
    attachments: Optional[List[Dict[str, Any]]] = None

class MedicalRecordUpdate(BaseSchema):
    record_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class MedicalRecord(MedicalRecordBase):
    id: int
    attachments: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Token schemas
class Token(BaseSchema):
    access_token: str
    token_type: str

class TokenData(BaseSchema):
    user_id: Optional[int] = None 