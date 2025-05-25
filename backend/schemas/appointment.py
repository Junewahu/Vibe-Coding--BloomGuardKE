from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from .base import BaseSchema
from .patient import Patient
from .user import User

class AppointmentBase(BaseModel):
    """Base appointment schema with common fields"""
    patient_id: int
    doctor_id: int
    appointment_type: str = Field(..., min_length=1, max_length=50)
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=180)
    notes: Optional[str] = Field(None, max_length=500)
    reminder_preferences: Optional[Dict[str, Any]] = None

class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment"""
    pass

class AppointmentUpdate(BaseModel):
    """Schema for updating an existing appointment"""
    doctor_id: Optional[int] = None
    appointment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    reminder_preferences: Optional[Dict[str, Any]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = Field(None, max_length=500)

class AppointmentInDB(AppointmentBase, BaseSchema):
    """Schema for appointment data in database"""
    status: str
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None

class Appointment(AppointmentInDB):
    """Schema for appointment response"""
    patient: Patient
    doctor: User
    is_past: bool
    is_upcoming: bool
    
    class Config:
        from_attributes = True 