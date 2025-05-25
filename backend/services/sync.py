from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import hashlib
import logging

from ..models.sync import (
    SyncQueue,
    SyncLog,
    OfflineCache,
    SyncConflict,
    SyncStatus,
    SyncType,
    SyncOperation,
    DeviceInfo
)
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.follow_up import FollowUp
from ..models.medical_record import MedicalRecord
from ..models.chw_visit import CHWVisit
from ..models.caregiver import Caregiver
from ..schemas.sync import (
    SyncRequest, SyncResponse, SyncStats,
    SyncQueueCreate, SyncStatusCreate, DeviceInfoCreate,
    SyncConflictCreate, OfflineCacheCreate
)

logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes in seconds
        self.max_offline_days = 3  # Maximum days of offline data

    async def sync_device(self, request: SyncRequest, user_id: int) -> SyncResponse:
        """Handle device sync request."""
        try:
            # Update device info
            device_info = await self._update_device_info(request.device_id, user_id)

            # Process pending changes from device
            if request.pending_changes:
                for change in request.pending_changes:
                    await self._process_pending_change(change, user_id)

            # Get changes to apply to device
            changes_to_apply = await self._get_changes_for_device(
                request.device_id,
                request.last_sync_time
            )

            # Get conflicts
            conflicts = await self._get_device_conflicts(request.device_id)

            # Get sync status
            sync_status = await self._get_sync_status(request.device_id)

            return SyncResponse(
                sync_time=datetime.utcnow(),
                changes_to_apply=changes_to_apply,
                conflicts=conflicts,
                sync_status=sync_status
            )

        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            raise

    async def _update_device_info(self, device_id: str, user_id: int) -> DeviceInfo:
        """Update or create device info."""
        try:
            device_info = self.db.query(DeviceInfo).filter(
                DeviceInfo.device_id == device_id
            ).first()

            if not device_info:
                device_info = DeviceInfo(
                    device_id=device_id,
                    user_id=user_id
                )
                self.db.add(device_info)

            device_info.last_sync_time = datetime.utcnow()
            self.db.commit()
            self.db.refresh(device_info)
            return device_info

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating device info: {str(e)}")
            raise

    async def _process_pending_change(
        self,
        change: SyncQueueCreate,
        user_id: int
    ) -> SyncQueue:
        """Process a pending change from device."""
        try:
            # Check for conflicts
            conflict = await self._check_for_conflicts(change)
            if conflict:
                return await self._handle_conflict(conflict, user_id)

            # Create sync queue entry
            sync_queue = SyncQueue(
                **change.dict(),
                user_id=user_id
            )
            self.db.add(sync_queue)

            # Update sync status
            sync_status = SyncStatus(
                entity_type=change.entity_type,
                entity_id=change.entity_id,
                status=SyncStatusEnum.SYNCING,
                device_id=change.device_id,
                user_id=user_id
            )
            self.db.add(sync_status)

            # Create sync log
            sync_log = SyncLog(
                device_id=change.device_id,
                sync_type=change.entity_type,
                operation=change.action,
                record_id=change.entity_id,
                status=SyncStatusEnum.SYNCING
            )
            self.db.add(sync_log)

            self.db.commit()
            self.db.refresh(sync_queue)
            return sync_queue

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing pending change: {str(e)}")
            raise

    async def _check_for_conflicts(self, change: SyncQueueCreate) -> Optional[SyncConflict]:
        """Check if a change conflicts with existing data."""
        try:
            # Get current sync status
            sync_status = self.db.query(SyncStatus).filter(
                SyncStatus.entity_type == change.entity_type,
                SyncStatus.entity_id == change.entity_id
            ).first()

            if not sync_status:
                return None

            # Get current data from cache
            cache = self.db.query(OfflineCache).filter(
                OfflineCache.cache_type == change.entity_type,
                OfflineCache.record_id == change.entity_id
            ).first()

            if not cache:
                return None

            # Check for version conflicts
            if cache.version != change.payload.get('version', 1):
                return SyncConflict(
                    record_type=change.entity_type,
                    record_id=change.entity_id,
                    server_version=cache.data,
                    client_version=change.payload
                )

            return None

        except Exception as e:
            logger.error(f"Error checking for conflicts: {str(e)}")
            raise

    async def _handle_conflict(
        self,
        conflict: SyncConflict,
        user_id: int
    ) -> SyncQueue:
        """Handle a sync conflict."""
        try:
            # Create conflict record
            db_conflict = SyncConflict(
                **conflict.dict(),
                user_id=user_id
            )
            self.db.add(db_conflict)

            # Update sync status
            sync_status = SyncStatus(
                entity_type=conflict.record_type,
                entity_id=conflict.record_id,
                status=SyncStatusEnum.CONFLICT,
                conflict_data=conflict.dict(),
                user_id=user_id
            )
            self.db.add(sync_status)

            self.db.commit()
            return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error handling conflict: {str(e)}")
            raise

    async def _get_changes_for_device(
        self,
        device_id: str,
        last_sync_time: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get changes to apply to device."""
        try:
            query = self.db.query(SyncQueue).filter(
                SyncQueue.device_id != device_id,
                SyncQueue.status == SyncStatusEnum.SYNCED
            )

            if last_sync_time:
                query = query.filter(SyncQueue.updated_at > last_sync_time)

            changes = query.all()
            return [self._format_change(change) for change in changes]

        except Exception as e:
            logger.error(f"Error getting changes for device: {str(e)}")
            raise

    async def _get_device_conflicts(self, device_id: str) -> List[Dict[str, Any]]:
        """Get conflicts for device."""
        try:
            conflicts = self.db.query(SyncConflict).filter(
                SyncConflict.device_id == device_id,
                SyncConflict.resolved_at == None
            ).all()
            return [self._format_conflict(conflict) for conflict in conflicts]

        except Exception as e:
            logger.error(f"Error getting device conflicts: {str(e)}")
            raise

    async def _get_sync_status(self, device_id: str) -> Dict[str, Any]:
        """Get sync status for device."""
        try:
            device_info = self.db.query(DeviceInfo).filter(
                DeviceInfo.device_id == device_id
            ).first()

            if not device_info:
                return {}

            pending = self.db.query(func.count(SyncQueue.id)).filter(
                SyncQueue.device_id == device_id,
                SyncQueue.status == SyncStatusEnum.PENDING
            ).scalar()

            synced = self.db.query(func.count(SyncQueue.id)).filter(
                SyncQueue.device_id == device_id,
                SyncQueue.status == SyncStatusEnum.SYNCED
            ).scalar()

            conflicts = self.db.query(func.count(SyncConflict.id)).filter(
                SyncConflict.device_id == device_id,
                SyncConflict.resolved_at == None
            ).scalar()

            return {
                "device_id": device_id,
                "last_sync": device_info.last_sync_time,
                "pending_changes": pending,
                "synced_changes": synced,
                "conflicts": conflicts
            }

        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            raise

    async def get_sync_stats(self, user_id: int) -> SyncStats:
        """Get sync statistics."""
        try:
            total_pending = self.db.query(func.count(SyncQueue.id)).filter(
                SyncQueue.user_id == user_id,
                SyncQueue.status == SyncStatusEnum.PENDING
            ).scalar()

            total_synced = self.db.query(func.count(SyncQueue.id)).filter(
                SyncQueue.user_id == user_id,
                SyncQueue.status == SyncStatusEnum.SYNCED
            ).scalar()

            total_conflicts = self.db.query(func.count(SyncConflict.id)).filter(
                SyncConflict.user_id == user_id,
                SyncConflict.resolved_at == None
            ).scalar()

            last_sync = self.db.query(DeviceInfo.last_sync_time).filter(
                DeviceInfo.user_id == user_id
            ).order_by(desc(DeviceInfo.last_sync_time)).first()

            sync_by_type = {}
            for sync_type in self.db.query(SyncQueue.entity_type).distinct():
                count = self.db.query(func.count(SyncQueue.id)).filter(
                    SyncQueue.user_id == user_id,
                    SyncQueue.entity_type == sync_type[0]
                ).scalar()
                sync_by_type[sync_type[0]] = count

            sync_by_status = {}
            for status in SyncStatusEnum:
                count = self.db.query(func.count(SyncQueue.id)).filter(
                    SyncQueue.user_id == user_id,
                    SyncQueue.status == status
                ).scalar()
                sync_by_status[status.value] = count

            return SyncStats(
                total_pending=total_pending,
                total_synced=total_synced,
                total_conflicts=total_conflicts,
                last_sync_time=last_sync[0] if last_sync else None,
                sync_by_type=sync_by_type,
                sync_by_status=sync_by_status
            )

        except Exception as e:
            logger.error(f"Error getting sync stats: {str(e)}")
            raise

    def _format_change(self, change: SyncQueue) -> Dict[str, Any]:
        """Format a change for response."""
        return {
            "id": change.id,
            "entity_type": change.entity_type,
            "entity_id": change.entity_id,
            "action": change.action.value,
            "payload": change.payload,
            "created_at": change.created_at.isoformat()
        }

    def _format_conflict(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Format a conflict for response."""
        return {
            "id": conflict.id,
            "record_type": conflict.record_type,
            "record_id": conflict.record_id,
            "server_version": conflict.server_version,
            "client_version": conflict.client_version,
            "created_at": conflict.created_at.isoformat()
        }

    async def queue_sync(
        self,
        db: Session,
        sync_type: SyncType,
        operation: SyncOperation,
        record_id: int,
        data: Dict[str, Any],
        device_id: str
    ) -> SyncQueue:
        """Queue a sync operation."""
        sync_queue = SyncQueue(
            sync_type=sync_type,
            operation=operation,
            record_id=record_id,
            data=data,
            device_id=device_id
        )
        db.add(sync_queue)
        db.commit()
        db.refresh(sync_queue)
        return sync_queue

    async def process_sync_queue(
        self,
        db: Session,
        device_id: str
    ) -> List[Dict[str, Any]]:
        """Process pending sync operations for a device."""
        pending_syncs = db.query(SyncQueue).filter(
            and_(
                SyncQueue.device_id == device_id,
                SyncQueue.status == SyncStatus.PENDING
            )
        ).all()

        results = []
        for sync in pending_syncs:
            try:
                # Start sync log
                sync_log = SyncLog(
                    device_id=device_id,
                    sync_type=sync.sync_type,
                    operation=sync.operation,
                    record_id=sync.record_id,
                    status=SyncStatus.IN_PROGRESS
                )
                db.add(sync_log)

                # Process sync
                sync.status = SyncStatus.IN_PROGRESS
                db.commit()

                # Apply sync operation
                result = await self._apply_sync_operation(db, sync)
                
                # Update sync status
                sync.status = SyncStatus.COMPLETED
                sync_log.status = SyncStatus.COMPLETED
                sync_log.completed_at = datetime.utcnow()
                
                results.append({
                    "sync_id": sync.id,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                # Handle failure
                sync.status = SyncStatus.FAILED
                sync.error_message = str(e)
                sync.retry_count += 1
                sync.last_retry = datetime.utcnow()
                
                sync_log.status = SyncStatus.FAILED
                sync_log.error_message = str(e)
                sync_log.completed_at = datetime.utcnow()
                
                results.append({
                    "sync_id": sync.id,
                    "status": "failed",
                    "error": str(e)
                })

            db.commit()

        return results

    async def _apply_sync_operation(
        self,
        db: Session,
        sync: SyncQueue
    ) -> Dict[str, Any]:
        """Apply a sync operation to the database."""
        # Get the appropriate model class
        model_class = self._get_model_class(sync.sync_type)
        if not model_class:
            raise ValueError(f"Invalid sync type: {sync.sync_type}")

        # Check for conflicts
        conflict = await self._check_conflict(db, sync)
        if conflict:
            return await self._handle_conflict(db, sync, conflict)

        # Apply the operation
        if sync.operation == SyncOperation.CREATE:
            return await self._create_record(db, model_class, sync.data)
        elif sync.operation == SyncOperation.UPDATE:
            return await self._update_record(db, model_class, sync.record_id, sync.data)
        elif sync.operation == SyncOperation.DELETE:
            return await self._delete_record(db, model_class, sync.record_id)
        else:
            raise ValueError(f"Invalid operation: {sync.operation}")

    def _get_model_class(self, sync_type: SyncType):
        """Get the SQLAlchemy model class for a sync type."""
        model_map = {
            SyncType.PATIENT: Patient,
            SyncType.APPOINTMENT: Appointment,
            SyncType.FOLLOW_UP: FollowUp,
            SyncType.MEDICAL_RECORD: MedicalRecord,
            SyncType.CHW_VISIT: CHWVisit,
            SyncType.CAREGIVER: Caregiver
        }
        return model_map.get(sync_type)

    async def _check_conflict(
        self,
        db: Session,
        sync: SyncQueue
    ) -> Optional[SyncConflict]:
        """Check for conflicts in sync operation."""
        if sync.operation == SyncOperation.CREATE:
            return None

        # Get server version
        model_class = self._get_model_class(sync.sync_type)
        server_record = db.query(model_class).filter(
            model_class.id == sync.record_id
        ).first()

        if not server_record:
            return None

        # Compare versions
        server_hash = self._hash_record(server_record)
        client_hash = self._hash_record(sync.data)

        if server_hash != client_hash:
            return SyncConflict(
                sync_queue_id=sync.id,
                record_type=sync.sync_type,
                record_id=sync.record_id,
                server_version=self._record_to_dict(server_record),
                client_version=sync.data
            )

        return None

    async def _handle_conflict(
        self,
        db: Session,
        sync: SyncQueue,
        conflict: SyncConflict
    ) -> Dict[str, Any]:
        """Handle a sync conflict."""
        # Store conflict
        db.add(conflict)
        sync.status = SyncStatus.CONFLICT
        db.commit()

        # Auto-resolve if possible
        if sync.operation == SyncOperation.UPDATE:
            # Use server version for critical fields
            critical_fields = self._get_critical_fields(sync.sync_type)
            resolved_data = {**sync.data}
            for field in critical_fields:
                if field in conflict.server_version:
                    resolved_data[field] = conflict.server_version[field]

            # Update conflict resolution
            conflict.resolution = {
                "auto_resolved": True,
                "strategy": "server_critical_fields",
                "resolved_data": resolved_data
            }
            conflict.resolved_at = datetime.utcnow()
            db.commit()

            # Apply resolved data
            return await self._update_record(
                db,
                self._get_model_class(sync.sync_type),
                sync.record_id,
                resolved_data
            )
        else:
            # Manual resolution required
            return {
                "status": "conflict",
                "conflict_id": conflict.id,
                "message": "Manual resolution required"
            }

    def _get_critical_fields(self, sync_type: SyncType) -> List[str]:
        """Get list of critical fields that should not be overwritten by client."""
        critical_fields_map = {
            SyncType.PATIENT: ["id", "created_at", "nhif_number"],
            SyncType.APPOINTMENT: ["id", "created_at", "doctor_id"],
            SyncType.FOLLOW_UP: ["id", "created_at", "patient_id"],
            SyncType.MEDICAL_RECORD: ["id", "created_at", "patient_id"],
            SyncType.CHW_VISIT: ["id", "created_at", "chw_id"],
            SyncType.CAREGIVER: ["id", "created_at", "patient_id"]
        }
        return critical_fields_map.get(sync_type, [])

    async def _create_record(
        self,
        db: Session,
        model_class,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record."""
        record = model_class(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return self._record_to_dict(record)

    async def _update_record(
        self,
        db: Session,
        model_class,
        record_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record."""
        record = db.query(model_class).filter(model_class.id == record_id).first()
        if not record:
            raise ValueError(f"Record not found: {record_id}")

        for key, value in data.items():
            setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return self._record_to_dict(record)

    async def _delete_record(
        self,
        db: Session,
        model_class,
        record_id: int
    ) -> Dict[str, Any]:
        """Delete a record."""
        record = db.query(model_class).filter(model_class.id == record_id).first()
        if not record:
            raise ValueError(f"Record not found: {record_id}")

        db.delete(record)
        db.commit()
        return {"status": "deleted", "id": record_id}

    def _hash_record(self, record: Any) -> str:
        """Generate a hash for a record."""
        if isinstance(record, dict):
            data = record
        else:
            data = self._record_to_dict(record)
        
        # Sort keys to ensure consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()

    def _record_to_dict(self, record: Any) -> Dict[str, Any]:
        """Convert a SQLAlchemy record to a dictionary."""
        if isinstance(record, dict):
            return record
        
        return {
            column.name: getattr(record, column.name)
            for column in record.__table__.columns
        }

    async def get_offline_data(
        self,
        db: Session,
        device_id: str,
        sync_type: Optional[SyncType] = None
    ) -> List[Dict[str, Any]]:
        """Get data for offline use."""
        query = db.query(OfflineCache).filter(
            and_(
                OfflineCache.device_id == device_id,
                OfflineCache.is_deleted == False
            )
        )

        if sync_type:
            query = query.filter(OfflineCache.cache_type == sync_type)

        # Get records updated in the last max_offline_days
        cutoff_date = datetime.utcnow() - timedelta(days=self.max_offline_days)
        query = query.filter(OfflineCache.last_synced >= cutoff_date)

        cache_records = query.all()
        return [record.data for record in cache_records]

    async def update_offline_cache(
        self,
        db: Session,
        device_id: str,
        sync_type: SyncType,
        record_id: int,
        data: Dict[str, Any]
    ) -> OfflineCache:
        """Update the offline cache for a record."""
        cache = db.query(OfflineCache).filter(
            and_(
                OfflineCache.device_id == device_id,
                OfflineCache.cache_type == sync_type,
                OfflineCache.record_id == record_id
            )
        ).first()

        if cache:
            cache.data = data
            cache.version += 1
            cache.last_synced = datetime.utcnow()
        else:
            cache = OfflineCache(
                device_id=device_id,
                cache_type=sync_type,
                record_id=record_id,
                data=data
            )
            db.add(cache)

        db.commit()
        db.refresh(cache)
        return cache

# Create singleton instance
sync_service = SyncService() 