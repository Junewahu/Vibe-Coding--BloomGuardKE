from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..models.sync import SyncType, SyncOperation, SyncStatus

class SyncAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncStatusEnum(str, Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"

class SyncQueueBase(BaseModel):
    entity_type: str
    entity_id: int
    action: SyncAction
    payload: Dict[str, Any]
    device_id: str

class SyncQueueCreate(SyncQueueBase):
    pass

class SyncQueueUpdate(BaseModel):
    status: Optional[SyncStatusEnum] = None
    error_message: Optional[str] = None

class SyncQueueResponse(SyncQueueBase):
    id: int
    status: SyncStatusEnum
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class SyncStatusBase(BaseModel):
    entity_type: str
    entity_id: int
    device_id: str

class SyncStatusCreate(SyncStatusBase):
    pass

class SyncStatusUpdate(BaseModel):
    status: Optional[SyncStatusEnum] = None
    last_synced_at: Optional[datetime] = None
    conflict_data: Optional[Dict[str, Any]] = None

class SyncStatusResponse(SyncStatusBase):
    id: int
    status: SyncStatusEnum
    last_synced_at: Optional[datetime]
    conflict_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class DeviceInfoBase(BaseModel):
    device_id: str
    device_type: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    is_active: bool = True

class DeviceInfoCreate(DeviceInfoBase):
    pass

class DeviceInfoUpdate(BaseModel):
    last_sync_time: Optional[datetime] = None
    device_type: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceInfoResponse(DeviceInfoBase):
    id: int
    last_sync_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class SyncLogBase(BaseModel):
    device_id: str
    sync_type: SyncType
    operation: SyncAction
    record_id: int
    status: SyncStatusEnum
    metadata: Optional[Dict[str, Any]] = None

class SyncLogCreate(SyncLogBase):
    pass

class SyncLogResponse(SyncLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        orm_mode = True

class OfflineCacheBase(BaseModel):
    device_id: str
    cache_type: SyncType
    record_id: int
    data: Dict[str, Any]
    version: int = 1
    is_deleted: bool = False
    metadata: Optional[Dict[str, Any]] = None

class OfflineCacheCreate(OfflineCacheBase):
    pass

class OfflineCacheUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    version: Optional[int] = None
    is_deleted: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class OfflineCacheResponse(OfflineCacheBase):
    id: int
    last_synced: datetime

    class Config:
        orm_mode = True

class SyncConflictBase(BaseModel):
    record_type: SyncType
    record_id: int
    server_version: Dict[str, Any]
    client_version: Dict[str, Any]

class SyncConflictCreate(SyncConflictBase):
    sync_queue_id: int

class SyncConflictUpdate(BaseModel):
    resolved_at: Optional[datetime] = None
    resolution: Optional[Dict[str, Any]] = None
    resolved_by: Optional[int] = None

class SyncConflictResponse(SyncConflictBase):
    id: int
    sync_queue_id: int
    created_at: datetime
    resolved_at: Optional[datetime]
    resolution: Optional[Dict[str, Any]]
    resolved_by: Optional[int]

    class Config:
        orm_mode = True

class SyncRequest(BaseModel):
    device_id: str
    last_sync_time: Optional[datetime] = None
    pending_changes: Optional[List[SyncQueueCreate]] = None

class SyncResponse(BaseModel):
    sync_time: datetime
    changes_to_apply: List[Dict[str, Any]]
    conflicts: List[SyncConflictResponse]
    sync_status: Dict[str, Any]

class SyncStats(BaseModel):
    total_pending: int
    total_synced: int
    total_conflicts: int
    last_sync_time: Optional[datetime]
    sync_by_type: Dict[str, int]
    sync_by_status: Dict[str, int]

class DeviceSyncStatus(BaseModel):
    device_id: str
    last_sync: Optional[datetime]
    sync_status: SyncStatus
    pending_operations: int
    conflicts: int
    offline_cache_size: int
    sync_stats: SyncStats 