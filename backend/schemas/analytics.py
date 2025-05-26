from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from ..models.analytics import (
    ReportType, ReportFormat, ReportStatus,
    MetricType, DashboardType
)

# Report schemas
class ReportBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportType
    format: ReportFormat
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: Optional[ReportType] = None
    format: Optional[ReportFormat] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportResponse(ReportBase):
    id: int
    status: ReportStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Metric schemas
class MetricBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metric_type: MetricType
    query: str
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MetricCreate(MetricBase):
    pass

class MetricUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    metric_type: Optional[MetricType] = None
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MetricResponse(MetricBase):
    id: int
    report_id: int
    value: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dashboard schemas
class DashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    dashboard_type: DashboardType
    layout: Dict[str, Any]
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = None

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    dashboard_type: Optional[DashboardType] = None
    layout: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class DashboardResponse(DashboardBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dashboard Widget schemas
class DashboardWidgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    widget_type: str = Field(..., min_length=1, max_length=50)
    configuration: Dict[str, Any]
    position: Dict[str, Any]
    refresh_interval: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class DashboardWidgetCreate(DashboardWidgetBase):
    pass

class DashboardWidgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    widget_type: Optional[str] = Field(None, min_length=1, max_length=50)
    configuration: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class DashboardWidgetResponse(DashboardWidgetBase):
    id: int
    dashboard_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Export schemas
class ExportBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    format: ReportFormat
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ExportCreate(ExportBase):
    pass

class ExportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    format: Optional[ReportFormat] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ExportResponse(ExportBase):
    id: int
    status: ReportStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Statistics schema
class AnalyticsStats(BaseModel):
    total_reports: int
    total_dashboards: int
    total_exports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    dashboards_by_type: Dict[str, int]
    exports_by_format: Dict[str, int]
    exports_by_status: Dict[str, int]
    recent_reports: List[ReportResponse]
    recent_exports: List[ExportResponse]
    popular_metrics: List[MetricResponse]
    public_dashboards: List[DashboardResponse]

class MetricType(str, Enum):
    MESSAGE_DELIVERY = "message_delivery"
    NHIF_CLAIM = "nhif_claim"
    PATIENT_ENGAGEMENT = "patient_engagement"
    FACILITY_PERFORMANCE = "facility_performance"

class TimeRange(BaseModel):
    start_date: datetime
    end_date: datetime

class MessageDeliveryMetricsBase(BaseModel):
    facility_id: int
    date: datetime
    channel: str
    total_sent: int = 0
    delivered: int = 0
    failed: int = 0
    pending: int = 0
    delivery_rate: float = 0.0
    average_delivery_time: float = 0.0

class MessageDeliveryMetricsCreate(MessageDeliveryMetricsBase):
    pass

class MessageDeliveryMetrics(MessageDeliveryMetricsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NHIFClaimMetricsBase(BaseModel):
    facility_id: int
    date: datetime
    total_claims: int = 0
    approved_claims: int = 0
    rejected_claims: int = 0
    pending_claims: int = 0
    total_amount_claimed: float = 0.0
    total_amount_approved: float = 0.0
    average_processing_time: float = 0.0
    approval_rate: float = 0.0

class NHIFClaimMetricsCreate(NHIFClaimMetricsBase):
    pass

class NHIFClaimMetrics(NHIFClaimMetricsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PatientEngagementMetricsBase(BaseModel):
    facility_id: int
    date: datetime
    total_patients: int = 0
    active_patients: int = 0
    new_patients: int = 0
    returning_patients: int = 0
    appointment_attendance_rate: float = 0.0
    message_response_rate: float = 0.0
    average_visits_per_patient: float = 0.0
    patient_satisfaction_score: float = 0.0

class PatientEngagementMetricsCreate(PatientEngagementMetricsBase):
    pass

class PatientEngagementMetrics(PatientEngagementMetricsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FacilityPerformanceMetricsBase(BaseModel):
    facility_id: int
    date: datetime
    total_appointments: int = 0
    completed_appointments: int = 0
    cancelled_appointments: int = 0
    no_show_appointments: int = 0
    average_wait_time: float = 0.0
    average_consultation_time: float = 0.0
    revenue: float = 0.0
    nhif_revenue: float = 0.0
    cash_revenue: float = 0.0

class FacilityPerformanceMetricsCreate(FacilityPerformanceMetricsBase):
    pass

class FacilityPerformanceMetrics(FacilityPerformanceMetricsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MetricsSummary(BaseModel):
    total_facilities: int
    total_patients: int
    total_claims: int
    total_revenue: float
    nhif_revenue: float
    cash_revenue: float
    message_delivery_rate: float
    claim_approval_rate: float
    patient_satisfaction_score: float
    average_wait_time: float 