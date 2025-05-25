from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..models.caregiver import (
    CaregiverType,
    CommunicationChannel,
    CommunicationStatus
)

class CaregiverBase(BaseModel):
    """Base caregiver schema with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    preferred_contact_method: str = Field(default="whatsapp", min_length=1, max_length=20)
    preferred_language: str = Field(default="en", min_length=2, max_length=10)
    notification_preferences: Optional[Dict[str, Any]] = None
    address: Optional[str] = Field(None, max_length=200)
    occupation: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    patient_id: int
    type: CaregiverType
    relationship: str
    is_primary: bool = False

class CaregiverCreate(CaregiverBase):
    """Schema for creating a new caregiver"""
    patient_ids: List[int]  # List of patient IDs to associate with this caregiver
    relationships: List[str]  # List of relationships corresponding to patient_ids

class CaregiverUpdate(BaseModel):
    """Schema for updating an existing caregiver"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    preferred_contact_method: Optional[str] = Field(None, min_length=1, max_length=20)
    preferred_language: Optional[str] = Field(None, min_length=2, max_length=10)
    notification_preferences: Optional[Dict[str, Any]] = None
    address: Optional[str] = Field(None, max_length=200)
    occupation: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    type: Optional[CaregiverType] = None
    relationship: Optional[str] = None
    is_primary: Optional[bool] = None

class CaregiverInDB(CaregiverBase):
    """Schema for caregiver data in database"""
    is_active: bool = True
    last_contact_date: Optional[datetime] = None

class Caregiver(CaregiverInDB):
    """Schema for caregiver response"""
    full_name: str
    primary_patients: List[int]
    
    class Config:
        from_attributes = True

class CaregiverResponse(CaregiverBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CommunicationBase(BaseModel):
    caregiver_id: int
    channel: CommunicationChannel
    template_name: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class CommunicationCreate(CommunicationBase):
    pass

class CommunicationResponse(CommunicationBase):
    id: int
    status: CommunicationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TemplateBase(BaseModel):
    name: str
    channel: CommunicationChannel
    content_type: str
    content: Dict[str, Any]
    variables: List[str]
    language: str = "en"
    is_active: bool = True

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    channel: Optional[CommunicationChannel] = None
    content_type: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None

class TemplateResponse(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EngagementBase(BaseModel):
    caregiver_id: int
    engagement_type: str
    response_time: Optional[int] = None
    interaction_data: Dict[str, Any]
    notes: Optional[str] = None

class EngagementCreate(EngagementBase):
    pass

class EngagementResponse(EngagementBase):
    id: int
    engagement_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BroadcastMessage(BaseModel):
    template_name: str
    caregiver_ids: List[int]
    variables: Dict[str, Any]
    channel: Optional[CommunicationChannel] = None
    schedule_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class VoiceNoteContent(BaseModel):
    audio_url: HttpUrl
    duration: int  # Duration in seconds
    transcription: Optional[str] = None
    language: str = "en"

class EngagementStats(BaseModel):
    total_communications: int
    successful_communications: int
    failed_communications: int
    average_response_time: Optional[int] = None
    engagement_rate: float
    channel_usage: Dict[CommunicationChannel, int]
    recent_engagements: List[EngagementResponse] 