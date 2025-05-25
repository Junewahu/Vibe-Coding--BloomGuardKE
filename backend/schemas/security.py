from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from ..models.security import (
    PermissionType, ResourceType
)

# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_system: bool = False
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permission_type: PermissionType
    resource_type: ResourceType
    resource_id: Optional[int] = None
    is_system: bool = False
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permission_type: Optional[PermissionType] = None
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# API Key schemas
class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    expires_at: Optional[datetime] = None
    ip_whitelist: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    ip_whitelist: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class APIKeyResponse(APIKeyBase):
    id: int
    user_id: int
    key: str  # Only the first few characters for security
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class APIKeyFullResponse(APIKeyResponse):
    secret: str  # Only included in the initial creation response

# Audit Log schemas
class AuditLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    resource_type: ResourceType
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = Field(..., min_length=1, max_length=50)
    error_message: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None
    api_key_id: Optional[int] = None

class AuditLogResponse(AuditLogBase):
    id: int
    user_id: Optional[int]
    api_key_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

# Security Policy schemas
class SecurityPolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    policy_type: str = Field(..., min_length=1, max_length=50)
    rules: Dict[str, Any]
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class SecurityPolicyCreate(SecurityPolicyBase):
    pass

class SecurityPolicyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    policy_type: Optional[str] = Field(None, min_length=1, max_length=50)
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityPolicyResponse(SecurityPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Statistics schema
class SecurityStats(BaseModel):
    total_roles: int
    total_permissions: int
    total_api_keys: int
    active_api_keys: int
    total_audit_logs: int
    audit_logs_by_action: Dict[str, int]
    audit_logs_by_status: Dict[str, int]
    recent_audit_logs: List[AuditLogResponse]
    security_policies: List[SecurityPolicyResponse]
    role_distribution: Dict[str, int]  # Number of users per role
    permission_distribution: Dict[str, int]  # Number of roles per permission 