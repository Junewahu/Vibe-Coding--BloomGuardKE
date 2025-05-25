from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.incentives import IncentivesService
from ..schemas.incentives import (
    RewardCreate,
    RewardUpdate,
    RewardResponse,
    AchievementCreate,
    AchievementUpdate,
    AchievementResponse,
    AdherenceTrackingCreate,
    AdherenceTrackingUpdate,
    AdherenceTrackingResponse,
    AdherenceCheckCreate,
    AdherenceCheckResponse,
    IncentiveProgramCreate,
    IncentiveProgramUpdate,
    IncentiveProgramResponse,
    ProgramEnrollmentCreate,
    ProgramEnrollmentUpdate,
    ProgramEnrollmentResponse,
    RewardStats,
    AchievementStats,
    AdherenceStats,
    ProgramStats
)
from ..auth import get_current_user
from ..models.incentives import RewardType, AchievementType, AdherenceStatus

router = APIRouter(
    prefix="/incentives",
    tags=["incentives"],
    dependencies=[Depends(get_current_user)]
)

# Reward Endpoints
@router.post("/rewards", response_model=RewardResponse)
async def create_reward(
    reward_data: RewardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new reward."""
    try:
        service = IncentivesService(db)
        return await service.create_reward(reward_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/rewards/{reward_id}", response_model=RewardResponse)
async def update_reward(
    reward_id: int,
    reward_data: RewardUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a reward."""
    try:
        service = IncentivesService(db)
        return await service.update_reward(reward_id, reward_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rewards", response_model=List[RewardResponse])
async def get_rewards(
    reward_type: Optional[RewardType] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get rewards with optional filters."""
    try:
        service = IncentivesService(db)
        return await service.get_rewards(
            chw_id=current_user.id,
            reward_type=reward_type,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Achievement Endpoints
@router.post("/achievements", response_model=AchievementResponse)
async def create_achievement(
    achievement_data: AchievementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new achievement."""
    try:
        service = IncentivesService(db)
        return await service.create_achievement(achievement_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/achievements/{achievement_id}", response_model=AchievementResponse)
async def update_achievement(
    achievement_id: int,
    achievement_data: AchievementUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an achievement."""
    try:
        service = IncentivesService(db)
        return await service.update_achievement(achievement_id, achievement_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    achievement_type: Optional[AchievementType] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get achievements with optional filters."""
    try:
        service = IncentivesService(db)
        return await service.get_achievements(
            chw_id=current_user.id,
            achievement_type=achievement_type,
            is_completed=is_completed
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Adherence Tracking Endpoints
@router.post("/adherence", response_model=AdherenceTrackingResponse)
async def create_adherence_tracking(
    tracking_data: AdherenceTrackingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new adherence tracking record."""
    try:
        service = IncentivesService(db)
        return await service.create_adherence_tracking(tracking_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/adherence/{tracking_id}", response_model=AdherenceTrackingResponse)
async def update_adherence_tracking(
    tracking_id: int,
    tracking_data: AdherenceTrackingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an adherence tracking record."""
    try:
        service = IncentivesService(db)
        return await service.update_adherence_tracking(tracking_id, tracking_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/adherence/checks", response_model=AdherenceCheckResponse)
async def create_adherence_check(
    check_data: AdherenceCheckCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new adherence check."""
    try:
        service = IncentivesService(db)
        return await service.create_adherence_check(check_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/adherence", response_model=List[AdherenceTrackingResponse])
async def get_adherence_tracking(
    patient_id: Optional[int] = None,
    status: Optional[AdherenceStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get adherence tracking records with optional filters."""
    try:
        service = IncentivesService(db)
        return await service.get_adherence_tracking(
            patient_id=patient_id,
            chw_id=current_user.id,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Incentive Program Endpoints
@router.post("/programs", response_model=IncentiveProgramResponse)
async def create_incentive_program(
    program_data: IncentiveProgramCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new incentive program."""
    try:
        service = IncentivesService(db)
        return await service.create_incentive_program(program_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/programs/{program_id}", response_model=IncentiveProgramResponse)
async def update_incentive_program(
    program_id: int,
    program_data: IncentiveProgramUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an incentive program."""
    try:
        service = IncentivesService(db)
        return await service.update_incentive_program(program_id, program_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/programs/enroll", response_model=ProgramEnrollmentResponse)
async def enroll_in_program(
    enrollment_data: ProgramEnrollmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Enroll a CHW in an incentive program."""
    try:
        service = IncentivesService(db)
        return await service.enroll_in_program(enrollment_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/programs/enrollments/{enrollment_id}", response_model=ProgramEnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    enrollment_data: ProgramEnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a program enrollment."""
    try:
        service = IncentivesService(db)
        return await service.update_enrollment(enrollment_id, enrollment_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Statistics Endpoints
@router.get("/stats/rewards", response_model=RewardStats)
async def get_reward_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get reward statistics."""
    try:
        service = IncentivesService(db)
        return await service.get_reward_stats(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/achievements", response_model=AchievementStats)
async def get_achievement_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get achievement statistics."""
    try:
        service = IncentivesService(db)
        return await service.get_achievement_stats(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/adherence", response_model=AdherenceStats)
async def get_adherence_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get adherence statistics."""
    try:
        service = IncentivesService(db)
        return await service.get_adherence_stats(
            current_user.id,
            start_date,
            end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/programs", response_model=ProgramStats)
async def get_program_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get program statistics."""
    try:
        service = IncentivesService(db)
        return await service.get_program_stats(
            current_user.id,
            start_date,
            end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 