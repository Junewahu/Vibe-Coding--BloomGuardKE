from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, date
from enum import Enum

from ..models.scheduling import ScheduleType, ScheduleStatus

# Schedule Rule schemas
class ScheduleRuleBase(BaseModel):
    rule_type: ScheduleType
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    conditions: Dict[str, Any]
    schedule_template: Dict[str, Any]
    is_active: bool = True

class ScheduleRuleCreate(ScheduleRuleBase):
    pass

class ScheduleRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    schedule_template: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ScheduleRuleResponse(ScheduleRuleBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Custom Protocol schemas
class CustomProtocolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    protocol_type: str
    steps: List[Dict[str, Any]]
    duration: int
    is_active: bool = True

class CustomProtocolCreate(CustomProtocolBase):
    pass

class CustomProtocolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    protocol_type: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None

class CustomProtocolResponse(CustomProtocolBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Follow-Up Schedule schemas
class FollowUpScheduleBase(BaseModel):
    patient_id: int
    schedule_type: ScheduleType
    rule_id: Optional[int] = None
    protocol_id: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    visits: List[Dict[str, Any]]
    adjustments: Optional[List[Dict[str, Any]]] = None

class FollowUpScheduleCreate(FollowUpScheduleBase):
    pass

class FollowUpScheduleUpdate(BaseModel):
    schedule_type: Optional[ScheduleType] = None
    rule_id: Optional[int] = None
    protocol_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ScheduleStatus] = None
    visits: Optional[List[Dict[str, Any]]] = None
    adjustments: Optional[List[Dict[str, Any]]] = None

class FollowUpScheduleResponse(FollowUpScheduleBase):
    id: int
    status: ScheduleStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Schedule Adjustment schemas
class ScheduleAdjustmentBase(BaseModel):
    schedule_id: int
    reason: str
    original_date: datetime
    new_date: datetime
    adjustment_type: str
    notes: Optional[str] = None

class ScheduleAdjustmentCreate(ScheduleAdjustmentBase):
    pass

class ScheduleAdjustmentUpdate(BaseModel):
    reason: Optional[str] = None
    new_date: Optional[datetime] = None
    adjustment_type: Optional[str] = None
    notes: Optional[str] = None

class ScheduleAdjustmentResponse(ScheduleAdjustmentBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Statistics schemas
class ScheduleStats(BaseModel):
    total_schedules: int
    schedules_by_type: Dict[str, int]
    schedules_by_status: Dict[str, int]
    average_duration: float
    completion_rate: float
    recent_adjustments: List[ScheduleAdjustmentResponse]
    active_protocols: List[CustomProtocolResponse]
    popular_rules: List[ScheduleRuleResponse]

class ScheduleBase(BaseModel):
    """Base schema for schedules"""
    patient_id: int
    rule_id: int
    scheduled_date: datetime
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ScheduleCreate(ScheduleBase):
    """Schema for creating a new schedule"""
    pass

class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule"""
    status: Optional[ScheduleStatus] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ScheduleResponse(ScheduleBase):
    """Schema for schedule response"""
    id: int
    status: ScheduleStatus
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleReminderBase(BaseModel):
    """Base schema for schedule reminders"""
    schedule_id: int
    reminder_date: datetime
    channel: str
    status: str
    response: Optional[Dict[str, Any]] = None

class ScheduleReminderCreate(ScheduleReminderBase):
    """Schema for creating a new schedule reminder"""
    pass

class ScheduleReminderUpdate(BaseModel):
    """Schema for updating a schedule reminder"""
    status: Optional[str] = None
    response: Optional[Dict[str, Any]] = None

class ScheduleReminderResponse(ScheduleReminderBase):
    """Schema for schedule reminder response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleTemplateBase(BaseModel):
    """Base schema for schedule templates"""
    name: str = Field(..., min_length=1, max_length=200)
    schedule_type: ScheduleType
    template: Dict[str, Any]
    is_active: bool = True

class ScheduleTemplateCreate(ScheduleTemplateBase):
    """Schema for creating a new schedule template"""
    pass

class ScheduleTemplateUpdate(BaseModel):
    """Schema for updating a schedule template"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    template: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ScheduleTemplateResponse(ScheduleTemplateBase):
    """Schema for schedule template response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleOverrideBase(BaseModel):
    """Base schema for schedule overrides"""
    schedule_id: int
    override_type: str
    reason: str
    new_date: Optional[datetime] = None
    created_by: int

class ScheduleOverrideCreate(ScheduleOverrideBase):
    """Schema for creating a new schedule override"""
    pass

class ScheduleOverrideResponse(ScheduleOverrideBase):
    """Schema for schedule override response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 