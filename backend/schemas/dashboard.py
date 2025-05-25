from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from ..models.dashboard import DashboardWidgetType

class DashboardWidgetBase(BaseModel):
    widget_type: DashboardWidgetType
    title: str = Field(..., min_length=1, max_length=100)
    position: int = Field(..., ge=0)
    size: str = Field(..., pattern="^(small|medium|large)$")
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True

class DashboardWidgetCreate(DashboardWidgetBase):
    pass

class DashboardWidgetUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[int] = Field(None, ge=0)
    size: Optional[str] = Field(None, pattern="^(small|medium|large)$")
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DashboardWidgetResponse(DashboardWidgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class StaffAvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    is_available: bool = True
    break_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    break_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

class StaffAvailabilityCreate(StaffAvailabilityBase):
    pass

class StaffAvailabilityUpdate(BaseModel):
    start_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    is_available: Optional[bool] = None
    break_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    break_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

class StaffAvailabilityResponse(StaffAvailabilityBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class StaffLeaveBase(BaseModel):
    start_date: datetime
    end_date: datetime
    leave_type: str = Field(..., min_length=1, max_length=50)
    reason: Optional[str] = None

class StaffLeaveCreate(StaffLeaveBase):
    pass

class StaffLeaveUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected)$")
    reason: Optional[str] = None

class StaffLeaveResponse(StaffLeaveBase):
    id: int
    user_id: int
    status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PerformanceMetricBase(BaseModel):
    date: datetime
    metric_type: str = Field(..., min_length=1, max_length=50)
    value: float
    target: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class PerformanceMetricCreate(PerformanceMetricBase):
    pass

class PerformanceMetricUpdate(BaseModel):
    value: Optional[float] = None
    target: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class PerformanceMetricResponse(PerformanceMetricBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DashboardNotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str
    notification_type: str = Field(..., min_length=1, max_length=50)
    metadata: Optional[Dict[str, Any]] = None

class DashboardNotificationCreate(DashboardNotificationBase):
    pass

class DashboardNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class DashboardNotificationResponse(DashboardNotificationBase):
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_appointments: int
    upcoming_appointments: int
    pending_responses: int
    pending_follow_ups: int
    performance_metrics: Dict[str, float]
    recent_notifications: List[DashboardNotificationResponse]
    staff_availability: List[StaffAvailabilityResponse]
    leave_requests: List[StaffLeaveResponse] 