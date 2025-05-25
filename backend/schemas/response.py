from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from ..models.response import ResponseType, ResponseChannel, ResponseStatus

class ResponseBase(BaseModel):
    notification_id: int
    patient_id: int
    response_type: ResponseType
    message: str
    metadata: Optional[Dict[str, Any]] = None
    language: str = "en"

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(BaseModel):
    status: Optional[ResponseStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class ResponseEscalationBase(BaseModel):
    response_id: int
    escalated_to_id: int
    reason: str
    notes: Optional[str] = None

class ResponseEscalationCreate(ResponseEscalationBase):
    pass

class ResponseEscalationResponse(ResponseEscalationBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ResponseResponse(ResponseBase):
    id: int
    status: ResponseStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalation: Optional[ResponseEscalationResponse] = None

    class Config:
        orm_mode = True

class PatientResponseBase(BaseModel):
    reminder_id: int
    patient_id: int
    response_type: ResponseType
    response_channel: ResponseChannel
    content: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    response_time: datetime
    metadata: Optional[Dict[str, Any]] = None

class PatientResponseCreate(PatientResponseBase):
    pass

class PatientResponseUpdate(BaseModel):
    status: Optional[ResponseStatus] = None
    processed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PatientResponseResponse(PatientResponseBase):
    id: int
    status: ResponseStatus
    processed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResponseFollowUpBase(BaseModel):
    response_id: int
    action_type: str
    status: str
    action_data: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None

class ResponseFollowUpCreate(ResponseFollowUpBase):
    pass

class ResponseFollowUpUpdate(BaseModel):
    status: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    error_message: Optional[str] = None

class ResponseFollowUpResponse(ResponseFollowUpBase):
    id: int
    completed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResponseTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    response_type: ResponseType
    channel: ResponseChannel
    content: str
    variables: Optional[Dict[str, Any]] = None
    language: str = "en"
    active: bool = True

class ResponseTemplateCreate(ResponseTemplateBase):
    pass

class ResponseTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    active: Optional[bool] = None

class ResponseTemplateResponse(ResponseTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResponseAnalyticsBase(BaseModel):
    date: datetime
    response_type: ResponseType
    channel: ResponseChannel
    count: int = 0
    success_rate: Optional[float] = None
    average_response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ResponseAnalyticsCreate(ResponseAnalyticsBase):
    pass

class ResponseAnalyticsUpdate(BaseModel):
    count: Optional[int] = None
    success_rate: Optional[float] = None
    average_response_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ResponseAnalyticsResponse(ResponseAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResponseStats(BaseModel):
    total_responses: int
    response_rate: float
    average_response_time: Optional[float] = None
    response_type_distribution: Dict[str, int]
    channel_distribution: Dict[str, int]
    success_rate: float
    recent_responses: List[PatientResponseResponse]
    pending_follow_ups: List[ResponseFollowUpResponse] 