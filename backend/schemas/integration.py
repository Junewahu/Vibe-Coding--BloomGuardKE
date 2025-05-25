from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from ..models.integration import (
    IntegrationType, IntegrationStatus,
    IntegrationAuthType
)

class IntegrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    integration_type: IntegrationType
    description: Optional[str] = None
    base_url: str = Field(..., max_length=500)
    auth_type: IntegrationAuthType
    auth_config: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class IntegrationCreate(IntegrationBase):
    pass

class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    base_url: Optional[str] = Field(None, max_length=500)
    auth_type: Optional[IntegrationAuthType] = None
    auth_config: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class IntegrationResponse(IntegrationBase):
    id: int
    status: IntegrationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class APIRouteBase(BaseModel):
    path: str = Field(..., max_length=500)
    method: str = Field(..., max_length=10)
    description: Optional[str] = None
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class APIRouteCreate(APIRouteBase):
    integration_id: int

class APIRouteUpdate(BaseModel):
    path: Optional[str] = Field(None, max_length=500)
    method: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class APIRouteResponse(APIRouteBase):
    id: int
    integration_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class APIRateLimitBase(BaseModel):
    route_id: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    requests_count: int = 0
    window_start: datetime
    window_end: datetime

class APIRateLimitCreate(APIRateLimitBase):
    pass

class APIRateLimitUpdate(BaseModel):
    requests_count: Optional[int] = None
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None

class APIRateLimitResponse(APIRateLimitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class APILogBase(BaseModel):
    route_id: int
    user_id: Optional[int] = None
    request_id: str = Field(..., max_length=100)
    method: str = Field(..., max_length=10)
    path: str = Field(..., max_length=500)
    request_headers: Optional[Dict[str, str]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class APILogCreate(APILogBase):
    pass

class APILogResponse(APILogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class APITransformationBase(BaseModel):
    route_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    transformation_type: str = Field(..., max_length=50)
    transformation_script: str
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class APITransformationCreate(APITransformationBase):
    pass

class APITransformationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    transformation_type: Optional[str] = Field(None, max_length=50)
    transformation_script: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class APITransformationResponse(APITransformationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class IntegrationStats(BaseModel):
    total_integrations: int
    integrations_by_type: Dict[str, int]
    integrations_by_status: Dict[str, int]
    total_routes: int
    active_routes: int
    total_requests: int
    requests_by_status: Dict[str, int]
    average_response_time: float
    recent_logs: List[APILogResponse]
    rate_limit_violations: int
    transformation_count: int 