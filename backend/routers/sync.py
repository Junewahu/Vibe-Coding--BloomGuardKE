from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models.sync import SyncType, SyncOperation, SyncStatus
from ..services.sync import sync_service, SyncService
from ..schemas.sync import (
    SyncQueueCreate,
    SyncQueueResponse,
    SyncLogResponse,
    OfflineCacheResponse,
    SyncConflictResponse,
    SyncRequest,
    SyncResponse,
    SyncStats,
    SyncStatusResponse,
    DeviceInfoResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/queue", response_model=SyncQueueResponse)
async def queue_sync(
    sync_data: SyncQueueCreate,
    device_id: str = Query(..., description="Unique identifier for the device"),
    db: Session = Depends(get_db)
):
    """Queue a sync operation."""
    try:
        sync_queue = await sync_service.queue_sync(
            db=db,
            sync_type=sync_data.sync_type,
            operation=sync_data.operation,
            record_id=sync_data.record_id,
            data=sync_data.data,
            device_id=device_id
        )
        return sync_queue
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process", response_model=List[Dict[str, Any]])
async def process_sync_queue(
    device_id: str = Query(..., description="Unique identifier for the device"),
    db: Session = Depends(get_db)
):
    """Process pending sync operations for a device."""
    try:
        results = await sync_service.process_sync_queue(db=db, device_id=device_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offline-data", response_model=List[Dict[str, Any]])
async def get_offline_data(
    device_id: str = Query(..., description="Unique identifier for the device"),
    sync_type: Optional[SyncType] = Query(None, description="Type of data to retrieve"),
    db: Session = Depends(get_db)
):
    """Get data for offline use."""
    try:
        data = await sync_service.get_offline_data(
            db=db,
            device_id=device_id,
            sync_type=sync_type
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/offline-cache", response_model=OfflineCacheResponse)
async def update_offline_cache(
    device_id: str = Query(..., description="Unique identifier for the device"),
    sync_type: SyncType = Query(..., description="Type of data being cached"),
    record_id: int = Query(..., description="ID of the record being cached"),
    data: Dict[str, Any] = Query(..., description="Data to cache"),
    db: Session = Depends(get_db)
):
    """Update the offline cache for a record."""
    try:
        cache = await sync_service.update_offline_cache(
            db=db,
            device_id=device_id,
            sync_type=sync_type,
            record_id=record_id,
            data=data
        )
        return cache
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conflicts", response_model=List[SyncConflictResponse])
async def get_conflicts(
    device_id: str = Query(..., description="Unique identifier for the device"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    db: Session = Depends(get_db)
):
    """Get sync conflicts for a device."""
    try:
        conflicts = db.query(SyncConflict).filter(
            SyncConflict.device_id == device_id
        )
        
        if resolved is not None:
            conflicts = conflicts.filter(
                SyncConflict.resolved_at.isnot(None) if resolved
                else SyncConflict.resolved_at.is_(None)
            )
        
        return conflicts.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conflicts/{conflict_id}/resolve", response_model=SyncConflictResponse)
async def resolve_conflict(
    conflict_id: int,
    resolution: Dict[str, Any] = Query(..., description="Resolution data"),
    db: Session = Depends(get_db)
):
    """Resolve a sync conflict."""
    try:
        conflict = db.query(SyncConflict).filter(
            SyncConflict.id == conflict_id
        ).first()
        
        if not conflict:
            raise HTTPException(status_code=404, detail="Conflict not found")
        
        if conflict.resolved_at:
            raise HTTPException(status_code=400, detail="Conflict already resolved")
        
        conflict.resolution = resolution
        conflict.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(conflict)
        
        return conflict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[SyncLogResponse])
async def get_sync_logs(
    device_id: str = Query(..., description="Unique identifier for the device"),
    sync_type: Optional[SyncType] = Query(None, description="Filter by sync type"),
    status: Optional[SyncStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get sync logs for a device."""
    try:
        logs = db.query(SyncLog).filter(
            SyncLog.device_id == device_id
        )
        
        if sync_type:
            logs = logs.filter(SyncLog.sync_type == sync_type)
        
        if status:
            logs = logs.filter(SyncLog.status == status)
        
        if start_date:
            logs = logs.filter(SyncLog.created_at >= start_date)
        
        if end_date:
            logs = logs.filter(SyncLog.created_at <= end_date)
        
        return logs.order_by(SyncLog.created_at.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=SyncResponse)
async def sync_device(
    request: SyncRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Sync device with server."""
    sync_service = SyncService(db)
    return await sync_service.sync_device(request, current_user.id)

@router.get("/stats", response_model=SyncStats)
async def get_sync_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sync statistics."""
    sync_service = SyncService(db)
    return await sync_service.get_sync_stats(current_user.id)

@router.get("/queue", response_model=List[SyncQueueResponse])
async def get_sync_queue(
    status: Optional[str] = None,
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sync queue entries."""
    sync_service = SyncService(db)
    return await sync_service.get_sync_queue(
        user_id=current_user.id,
        status=status,
        device_id=device_id
    )

@router.get("/status", response_model=List[SyncStatusResponse])
async def get_sync_status(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sync status for entities."""
    sync_service = SyncService(db)
    return await sync_service.get_sync_status(
        user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id
    )

@router.get("/devices", response_model=List[DeviceInfoResponse])
async def get_devices(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get registered devices."""
    sync_service = SyncService(db)
    return await sync_service.get_devices(
        user_id=current_user.id,
        active_only=active_only
    )

@router.post("/devices", response_model=DeviceInfoResponse)
async def register_device(
    device_info: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Register a new device."""
    sync_service = SyncService(db)
    return await sync_service.register_device(
        device_info=device_info,
        user_id=current_user.id
    )

@router.put("/devices/{device_id}")
async def update_device(
    device_id: str,
    device_info: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update device information."""
    sync_service = SyncService(db)
    return await sync_service.update_device(
        device_id=device_id,
        device_info=device_info,
        user_id=current_user.id
    ) 