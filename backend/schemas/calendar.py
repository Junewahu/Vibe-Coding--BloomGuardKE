from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from ..models.calendar import EventType

class CalendarEventBase(BaseModel):
    event_type: EventType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    location: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CalendarEventCreate(CalendarEventBase):
    schedule_id: Optional[int] = None
    appointment_id: Optional[int] = None
    follow_up_id: Optional[int] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CalendarEventResponse(CalendarEventBase):
    id: int
    schedule_id: Optional[int] = None
    appointment_id: Optional[int] = None
    follow_up_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 