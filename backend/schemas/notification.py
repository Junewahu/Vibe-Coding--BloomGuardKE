from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from ..models.notification import (
    NotificationType, NotificationChannel,
    NotificationStatus, NotificationPriority
)

# Template schemas
class NotificationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    channel: NotificationChannel
    language: str = Field(..., min_length=2, max_length=2)  # ISO 639-1 language code
    template_text: str
    variables: Optional[Dict[str, Any]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    template_text: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Notification schemas
class NotificationBase(BaseModel):
    patient_id: int
    channel: NotificationChannel
    template_id: Optional[int] = None
    content: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    scheduled_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    response: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    read_time: Optional[datetime] = None
    response: Optional[Dict[str, Any]] = None
    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Notification Preference schemas
class NotificationPreferenceBase(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    is_enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: int

class NotificationPreferenceUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Notification Log schemas
class NotificationLogBase(BaseModel):
    channel: NotificationChannel
    status: NotificationStatus
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationLogCreate(NotificationLogBase):
    notification_id: int

class NotificationLogResponse(NotificationLogBase):
    id: int
    notification_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# WhatsApp Session schemas
class WhatsAppSessionBase(BaseModel):
    patient_id: int
    phone_number: str
    session_id: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class WhatsAppSessionCreate(WhatsAppSessionBase):
    pass

class WhatsAppSessionUpdate(BaseModel):
    status: Optional[str] = None
    last_interaction: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class WhatsAppSessionResponse(WhatsAppSessionBase):
    id: int
    last_interaction: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Voice Call schemas
class VoiceCallBase(BaseModel):
    patient_id: int
    phone_number: str
    call_id: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class VoiceCallCreate(VoiceCallBase):
    pass

class VoiceCallUpdate(BaseModel):
    status: Optional[str] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VoiceCallResponse(VoiceCallBase):
    id: int
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# USSD Menu schemas
class USSDMenuBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    menu_text: str
    options: Dict[str, Any]
    is_active: bool = True

class USSDMenuCreate(USSDMenuBase):
    pass

class USSDMenuUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    menu_text: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class USSDMenuResponse(USSDMenuBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# USSD Session schemas
class USSDSessionBase(BaseModel):
    patient_id: int
    phone_number: str
    session_id: str
    menu_id: int
    current_state: str
    input_history: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class USSDSessionCreate(USSDSessionBase):
    pass

class USSDSessionUpdate(BaseModel):
    current_state: Optional[str] = None
    input_history: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class USSDSessionResponse(USSDSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Statistics schema
class NotificationStats(BaseModel):
    total_notifications: int
    notifications_by_channel: Dict[str, int]
    notifications_by_status: Dict[str, int]
    average_response_time: Optional[float]
    success_rate: float
    recent_notifications: List[NotificationResponse]
    active_channels: List[str]
    popular_templates: List[NotificationTemplateResponse] 