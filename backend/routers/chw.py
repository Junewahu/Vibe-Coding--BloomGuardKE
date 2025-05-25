from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models.chw import VisitStatus, VisitType, CHWStatus
from ..services.chw import chw_service
from ..schemas.chw import (
    CHWCreate,
    CHWUpdate,
    CHWResponse,
    VisitCreate,
    VisitUpdate,
    VisitResponse,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    PerformanceCreate,
    PerformanceResponse,
    TrainingCreate,
    TrainingResponse,
    CHWStats
)

router = APIRouter(prefix="/chws", tags=["chws"])

@router.post("/", response_model=CHWResponse)
async def create_chw(
    chw: CHWCreate,
    db: Session = Depends(get_db)
):
    """Create a new CHW."""
    try:
        return await chw_service.create_chw(db, chw.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chw_id}", response_model=CHWResponse)
async def get_chw(
    chw_id: int,
    db: Session = Depends(get_db)
):
    """Get a CHW by ID."""
    chw = await chw_service.get_chw(db, chw_id)
    if not chw:
        raise HTTPException(status_code=404, detail="CHW not found")
    return chw

@router.put("/{chw_id}", response_model=CHWResponse)
async def update_chw(
    chw_id: int,
    chw_update: CHWUpdate,
    db: Session = Depends(get_db)
):
    """Update a CHW's information."""
    chw = await chw_service.update_chw(
        db,
        chw_id,
        chw_update.dict(exclude_unset=True)
    )
    if not chw:
        raise HTTPException(status_code=404, detail="CHW not found")
    return chw

@router.post("/{chw_id}/visits", response_model=VisitResponse)
async def create_visit(
    chw_id: int,
    visit: VisitCreate,
    db: Session = Depends(get_db)
):
    """Create a new visit for a CHW."""
    try:
        visit_data = visit.dict()
        visit_data["chw_id"] = chw_id
        return await chw_service.create_visit(db, visit_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/visits/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db)
):
    """Update a visit."""
    visit = await chw_service.update_visit(
        db,
        visit_id,
        visit_update.dict(exclude_unset=True)
    )
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.get("/{chw_id}/visits", response_model=List[VisitResponse])
async def get_visits(
    chw_id: int,
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[VisitStatus] = Query(None, description="Filter by visit status"),
    visit_type: Optional[VisitType] = Query(None, description="Filter by visit type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get visits for a CHW with filters."""
    visits = await chw_service.get_visits(
        db,
        chw_id=chw_id,
        patient_id=patient_id,
        status=status,
        visit_type=visit_type,
        start_date=start_date,
        end_date=end_date
    )
    return visits

@router.post("/{chw_id}/assignments", response_model=AssignmentResponse)
async def create_assignment(
    chw_id: int,
    assignment: AssignmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new assignment for a CHW."""
    try:
        assignment_data = assignment.dict()
        assignment_data["chw_id"] = chw_id
        return await chw_service.create_assignment(db, assignment_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an assignment."""
    assignment = await chw_service.update_assignment(
        db,
        assignment_id,
        assignment_update.dict(exclude_unset=True)
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.get("/{chw_id}/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    chw_id: int,
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by assignment status"),
    active_only: bool = Query(True, description="Show only active assignments"),
    db: Session = Depends(get_db)
):
    """Get assignments for a CHW with filters."""
    assignments = await chw_service.get_assignments(
        db,
        chw_id=chw_id,
        patient_id=patient_id,
        status=status,
        active_only=active_only
    )
    return assignments

@router.post("/{chw_id}/performance", response_model=PerformanceResponse)
async def create_performance(
    chw_id: int,
    performance: PerformanceCreate,
    db: Session = Depends(get_db)
):
    """Create new performance metrics for a CHW."""
    try:
        performance_data = performance.dict()
        performance_data["chw_id"] = chw_id
        return await chw_service.create_performance(db, performance_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chw_id}/performance", response_model=List[PerformanceResponse])
async def get_performance(
    chw_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a CHW."""
    performance = await chw_service.get_performance(
        db,
        chw_id,
        start_date=start_date,
        end_date=end_date
    )
    return performance

@router.post("/{chw_id}/training", response_model=TrainingResponse)
async def create_training(
    chw_id: int,
    training: TrainingCreate,
    db: Session = Depends(get_db)
):
    """Create a new training record for a CHW."""
    try:
        training_data = training.dict()
        training_data["chw_id"] = chw_id
        return await chw_service.create_training(db, training_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chw_id}/training", response_model=List[TrainingResponse])
async def get_training(
    chw_id: int,
    status: Optional[str] = Query(None, description="Filter by training status"),
    active_only: bool = Query(True, description="Show only active training records"),
    db: Session = Depends(get_db)
):
    """Get training records for a CHW."""
    training = await chw_service.get_training(
        db,
        chw_id,
        status=status,
        active_only=active_only
    )
    return training

@router.get("/{chw_id}/stats", response_model=CHWStats)
async def get_chw_stats(
    chw_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics for a CHW."""
    try:
        return await chw_service.get_chw_stats(
            db,
            chw_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 