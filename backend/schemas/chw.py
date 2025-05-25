from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..models.chw import (
    VisitStatus,
    VisitType,
    CHWStatus
)

class CHWBase(BaseModel):
    """Base CHW schema with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    assigned_area: str = Field(..., min_length=1, max_length=200)
    qualifications: List[Dict[str, Any]] = Field(default_factory=list)
    training_history: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = Field(None, max_length=500)
    status: CHWStatus = CHWStatus.ACTIVE

class CHWCreate(CHWBase):
    """Schema for creating a new CHW"""
    user_id: int

class CHWUpdate(BaseModel):
    """Schema for updating an existing CHW"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    assigned_area: Optional[str] = Field(None, min_length=1, max_length=200)
    qualifications: Optional[List[Dict[str, Any]]] = None
    training_history: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[CHWStatus] = None

class CHWResponse(CHWBase):
    """Schema for CHW response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class VisitBase(BaseModel):
    """Base schema for CHW visits"""
    chw_id: int
    patient_id: int
    visit_type: VisitType
    scheduled_date: datetime
    location: Dict[str, Any]
    notes: Optional[str] = None

class VisitCreate(VisitBase):
    """Schema for creating a new visit"""
    pass

class VisitUpdate(BaseModel):
    """Schema for updating a visit"""
    status: Optional[VisitStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = None
    notes: Optional[str] = None

class VisitResponse(VisitBase):
    """Schema for visit response"""
    id: int
    status: VisitStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    """Base schema for CHW assignments"""
    chw_id: int
    patient_id: int
    assignment_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    """Schema for creating a new assignment"""
    pass

class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment"""
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AssignmentResponse(AssignmentBase):
    """Schema for assignment response"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PerformanceBase(BaseModel):
    """Base schema for CHW performance metrics"""
    chw_id: int
    metric_date: datetime
    visits_completed: int = 0
    patients_served: int = 0
    follow_ups_completed: int = 0
    emergency_visits: int = 0
    average_response_time: Optional[float] = None
    patient_satisfaction: Optional[float] = None
    compliance_rate: Optional[float] = None
    notes: Optional[str] = None

class PerformanceCreate(PerformanceBase):
    """Schema for creating new performance metrics"""
    pass

class PerformanceUpdate(BaseModel):
    """Schema for updating performance metrics"""
    visits_completed: Optional[int] = None
    patients_served: Optional[int] = None
    follow_ups_completed: Optional[int] = None
    emergency_visits: Optional[int] = None
    average_response_time: Optional[float] = None
    patient_satisfaction: Optional[float] = None
    compliance_rate: Optional[float] = None
    notes: Optional[str] = None

class PerformanceResponse(PerformanceBase):
    """Schema for performance metrics response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TrainingBase(BaseModel):
    """Base schema for CHW training records"""
    chw_id: int
    training_name: str
    training_type: str
    provider: str
    start_date: datetime
    end_date: datetime
    status: str
    certification_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class TrainingCreate(TrainingBase):
    """Schema for creating a new training record"""
    pass

class TrainingUpdate(BaseModel):
    """Schema for updating a training record"""
    status: Optional[str] = None
    certification_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class TrainingResponse(TrainingBase):
    """Schema for training record response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CHWStats(BaseModel):
    """Schema for CHW statistics"""
    total_visits: int
    completed_visits: int
    pending_visits: int
    patients_served: int
    average_response_time: float
    patient_satisfaction: float
    compliance_rate: float
    recent_visits: List[VisitResponse]
    upcoming_visits: List[VisitResponse]
    performance_trend: Dict[str, Any] 