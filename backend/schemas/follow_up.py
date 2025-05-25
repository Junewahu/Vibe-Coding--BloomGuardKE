from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.follow_up import FollowUpType, FollowUpStatus

class FollowUpBase(BaseModel):
    patient_id: int
    doctor_id: int
    follow_up_type: FollowUpType
    scheduled_date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=180)
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    status: Optional[FollowUpStatus] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    reminder_sent: Optional[bool] = None

class FollowUpResponse(FollowUpBase):
    id: int
    status: FollowUpStatus
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 