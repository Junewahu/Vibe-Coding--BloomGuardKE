from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.chw_tracker import CHWTrackerService
from ..schemas.chw_tracker import (
    CHWFieldVisitCreate,
    CHWFieldVisitUpdate,
    CHWFieldVisitResponse,
    CHWActivityCreate,
    CHWActivityUpdate,
    CHWActivityResponse,
    CHWLocationTrackingCreate,
    CHWLocationTrackingResponse,
    CHWVisitStats,
    CHWActivityStats,
    CHWLocationStats
)
from ..auth import get_current_user
from ..models.chw_tracker import VisitStatus

router = APIRouter(
    prefix="/chw-tracker",
    tags=["chw-tracker"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/visits", response_model=CHWFieldVisitResponse)
async def create_field_visit(
    visit_data: CHWFieldVisitCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new field visit."""
    try:
        service = CHWTrackerService(db)
        return await service.create_field_visit(visit_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/visits/{visit_id}", response_model=CHWFieldVisitResponse)
async def update_field_visit(
    visit_id: int,
    visit_data: CHWFieldVisitUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a field visit."""
    try:
        service = CHWTrackerService(db)
        return await service.update_field_visit(visit_id, visit_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/visits", response_model=List[CHWFieldVisitResponse])
async def get_field_visits(
    patient_id: Optional[int] = None,
    status: Optional[VisitStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get field visits with optional filters."""
    try:
        service = CHWTrackerService(db)
        return await service.get_field_visits(
            chw_id=current_user.id,
            patient_id=patient_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/activities", response_model=CHWActivityResponse)
async def create_activity(
    activity_data: CHWActivityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new activity for a field visit."""
    try:
        service = CHWTrackerService(db)
        return await service.create_activity(activity_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/activities/{activity_id}", response_model=CHWActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: CHWActivityUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an activity."""
    try:
        service = CHWTrackerService(db)
        return await service.update_activity(activity_id, activity_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/location", response_model=CHWLocationTrackingResponse)
async def track_location(
    location_data: CHWLocationTrackingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Track CHW location during a visit."""
    try:
        service = CHWTrackerService(db)
        return await service.track_location(location_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/visits", response_model=CHWVisitStats)
async def get_visit_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for CHW visits."""
    try:
        service = CHWTrackerService(db)
        return await service.get_visit_stats(
            chw_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/activities", response_model=CHWActivityStats)
async def get_activity_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for CHW activities."""
    try:
        service = CHWTrackerService(db)
        return await service.get_activity_stats(
            chw_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/location", response_model=CHWLocationStats)
async def get_location_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for CHW location tracking."""
    try:
        service = CHWTrackerService(db)
        return await service.get_location_stats(
            chw_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 