from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..models.reminder import ReminderChannel, ReminderStatus, ReminderPriority

class ReminderBase(BaseModel):
    schedule_id: int
    patient_id: int
    channel: ReminderChannel
    priority: ReminderPriority = ReminderPriority.MEDIUM
    content: str
    scheduled_time: datetime
    metadata: Optional[Dict[str, Any]] = None

class ReminderCreate(ReminderBase):
    template_id: Optional[int] = None
    max_retries: Optional[int] = 3

class ReminderUpdate(BaseModel):
    status: Optional[ReminderStatus] = None
    content: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    priority: Optional[ReminderPriority] = None
    metadata: Optional[Dict[str, Any]] = None

class ReminderResponse(BaseModel):
    id: int
    schedule_id: int
    patient_id: int
    channel: ReminderChannel
    status: ReminderStatus
    priority: ReminderPriority
    content: str
    scheduled_time: datetime
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReminderResponseBase(BaseModel):
    response_type: str
    response_data: Optional[Dict[str, Any]] = None
    response_time: datetime

class ReminderResponseCreate(ReminderResponseBase):
    reminder_id: int

class ReminderResponseUpdate(BaseModel):
    response_type: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    response_time: Optional[datetime] = None

class ReminderResponseResponse(ReminderResponseBase):
    id: int
    reminder_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReminderTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    channel: ReminderChannel
    content_type: str
    content: str
    variables: Optional[Dict[str, Any]] = None
    language: str = "en"
    active: bool = True

class ReminderTemplateCreate(ReminderTemplateBase):
    pass

class ReminderTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    content_type: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    active: Optional[bool] = None

class ReminderTemplateResponse(ReminderTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReminderDeliveryLogBase(BaseModel):
    reminder_id: int
    attempt_number: int
    channel: ReminderChannel
    status: ReminderStatus
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None

class ReminderDeliveryLogCreate(ReminderDeliveryLogBase):
    pass

class ReminderDeliveryLogUpdate(BaseModel):
    status: Optional[ReminderStatus] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None

class ReminderDeliveryLogResponse(ReminderDeliveryLogBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReminderProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    channel: ReminderChannel
    api_key: str
    api_secret: str
    configuration: Optional[Dict[str, Any]] = None
    active: bool = True

class ReminderProviderCreate(ReminderProviderBase):
    pass

class ReminderProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None

class ReminderProviderResponse(ReminderProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReminderStats(BaseModel):
    total_reminders: int
    pending_reminders: int
    sent_reminders: int
    delivered_reminders: int
    failed_reminders: int
    delivery_rate: float
    average_delivery_time: Optional[float] = None
    channel_distribution: Dict[str, int]
    recent_reminders: List[ReminderResponse]
    upcoming_reminders: List[ReminderResponse] 