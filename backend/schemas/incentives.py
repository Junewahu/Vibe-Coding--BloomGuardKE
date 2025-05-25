from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema

class RewardType(str, Enum):
    MONETARY = "monetary"
    POINTS = "points"
    BADGE = "badge"
    CERTIFICATE = "certificate"
    OTHER = "other"

class AchievementType(str, Enum):
    VISIT_COUNT = "visit_count"
    PATIENT_COUNT = "patient_count"
    ADHERENCE_RATE = "adherence_rate"
    QUALITY_SCORE = "quality_score"
    TRAINING_COMPLETION = "training_completion"
    REFERRAL_COUNT = "referral_count"
    OTHER = "other"

class AdherenceStatus(str, Enum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

# Reward Schemas
class RewardBase(BaseModel):
    reward_type: RewardType
    amount: Optional[float] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None

class RewardCreate(RewardBase):
    chw_id: int

class RewardUpdate(BaseModel):
    status: Optional[str] = None
    distribution_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class RewardResponse(RewardBase):
    id: int
    chw_id: int
    status: str
    distribution_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Achievement Schemas
class AchievementBase(BaseModel):
    achievement_type: AchievementType
    title: str
    description: Optional[str] = None
    criteria: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class AchievementCreate(AchievementBase):
    chw_id: int

class AchievementUpdate(BaseModel):
    progress: Optional[float] = None
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class AchievementResponse(AchievementBase):
    id: int
    chw_id: int
    progress: float
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Adherence Tracking Schemas
class AdherenceTrackingBase(BaseModel):
    patient_id: int
    treatment_plan_id: int
    status: AdherenceStatus = AdherenceStatus.UNKNOWN
    adherence_rate: Optional[float] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AdherenceTrackingCreate(AdherenceTrackingBase):
    chw_id: int
    next_check_date: datetime

class AdherenceTrackingUpdate(BaseModel):
    status: Optional[AdherenceStatus] = None
    adherence_rate: Optional[float] = None
    last_check_date: Optional[datetime] = None
    next_check_date: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AdherenceTrackingResponse(AdherenceTrackingBase):
    id: int
    chw_id: int
    last_check_date: Optional[datetime]
    next_check_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Adherence Check Schemas
class AdherenceCheckBase(BaseModel):
    check_date: datetime
    is_compliant: bool
    notes: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

class AdherenceCheckCreate(AdherenceCheckBase):
    adherence_id: int

class AdherenceCheckUpdate(BaseModel):
    is_compliant: Optional[bool] = None
    notes: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

class AdherenceCheckResponse(AdherenceCheckBase):
    id: int
    adherence_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Incentive Program Schemas
class IncentiveProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    criteria: Dict[str, Any]
    rewards: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class IncentiveProgramCreate(IncentiveProgramBase):
    pass

class IncentiveProgramUpdate(BaseModel):
    description: Optional[str] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    criteria: Optional[Dict[str, Any]] = None
    rewards: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class IncentiveProgramResponse(IncentiveProgramBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Program Enrollment Schemas
class ProgramEnrollmentBase(BaseModel):
    program_id: int
    enrollment_date: datetime
    metadata: Optional[Dict[str, Any]] = None

class ProgramEnrollmentCreate(ProgramEnrollmentBase):
    chw_id: int

class ProgramEnrollmentUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    rewards_earned: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ProgramEnrollmentResponse(ProgramEnrollmentBase):
    id: int
    chw_id: int
    status: str
    progress: float
    rewards_earned: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Statistics Schemas
class RewardStats(BaseModel):
    total_rewards: int
    rewards_by_type: Dict[str, int]
    total_value: float
    distribution_rate: float

class AchievementStats(BaseModel):
    total_achievements: int
    completed_achievements: int
    achievements_by_type: Dict[str, int]
    average_completion_time: float

class AdherenceStats(BaseModel):
    total_patients: int
    compliance_rate: float
    status_distribution: Dict[str, int]
    average_adherence_rate: float

class ProgramStats(BaseModel):
    active_programs: int
    total_enrollments: int
    completion_rate: float
    average_progress: float 