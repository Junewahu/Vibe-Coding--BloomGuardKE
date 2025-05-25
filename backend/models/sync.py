from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import enum

from ..database import Base

class SyncAction(PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncStatusEnum(PyEnum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"

class SyncType(str, enum.Enum):
    PATIENT = "patient"
    APPOINTMENT = "appointment"
    FOLLOW_UP = "follow_up"
    MEDICAL_RECORD = "medical_record"
    CHW_VISIT = "chw_visit"
    CAREGIVER = "caregiver"

class SyncQueue(Base):
    """Model for tracking sync operations"""
    __tablename__ = "sync_queue"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # e.g., patient, visit, record
    entity_id = Column(Integer, nullable=False)
    action = Column(Enum(SyncAction), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(Enum(SyncStatusEnum), default=SyncStatusEnum.PENDING)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    device_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="sync_queue")

class SyncStatus(Base):
    __tablename__ = "sync_status"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    status = Column(Enum(SyncStatusEnum), default=SyncStatusEnum.PENDING)
    last_synced_at = Column(DateTime)
    conflict_data = Column(JSON)
    device_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sync_status")

class DeviceInfo(Base):
    __tablename__ = "device_info"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_sync_time = Column(DateTime)
    device_type = Column(String)
    os_version = Column(String)
    app_version = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="device_info")

class SyncLog(Base):
    """Model for tracking sync history"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100))
    sync_type = Column(Enum(SyncType))
    operation = Column(Enum(SyncAction))
    record_id = Column(Integer)
    status = Column(Enum(SyncStatusEnum))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional sync metadata

class OfflineCache(Base):
    """Model for storing offline data cache"""
    __tablename__ = "offline_cache"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100))
    cache_type = Column(Enum(SyncType))
    record_id = Column(Integer)
    data = Column(JSON)
    version = Column(Integer, default=1)  # For optimistic locking
    last_synced = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)  # Cache-specific metadata

class SyncConflict(Base):
    """Model for tracking sync conflicts"""
    __tablename__ = "sync_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    sync_queue_id = Column(Integer, ForeignKey("sync_queue.id"))
    record_type = Column(Enum(SyncType))
    record_id = Column(Integer)
    server_version = Column(JSON)  # Server's version of the record
    client_version = Column(JSON)  # Client's version of the record
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(JSON, nullable=True)  # How the conflict was resolved
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    sync_queue = relationship("SyncQueue")
    resolver = relationship("User") 