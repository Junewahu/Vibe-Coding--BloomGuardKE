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

class IncentiveType(str, Enum):
    PERFORMANCE = "performance"
    ATTENDANCE = "attendance"
    PATIENT_SATISFACTION = "patient_satisfaction"
    QUALITY_CARE = "quality_care"
    SPECIAL_ACHIEVEMENT = "special_achievement"

class IncentiveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"

class IncentivePeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

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

# Incentive Rule Schemas
class IncentiveRuleBase(BaseModel):
    facility_id: int
    incentive_type: IncentiveType
    period: IncentivePeriod
    name: str
    description: str
    target_metric: str
    target_value: float
    base_amount: float
    bonus_multiplier: float
    is_active: bool = True
    start_date: datetime
    end_date: Optional[datetime] = None

class IncentiveRuleCreate(IncentiveRuleBase):
    pass

class IncentiveRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_metric: Optional[str] = None
    target_value: Optional[float] = None
    base_amount: Optional[float] = None
    bonus_multiplier: Optional[float] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None

class IncentiveRule(IncentiveRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Incentive Schemas
class IncentiveBase(BaseModel):
    facility_id: int
    user_id: int
    incentive_type: IncentiveType
    period: IncentivePeriod
    start_date: datetime
    end_date: datetime
    target_value: float
    achieved_value: float
    base_amount: float
    bonus_amount: float
    total_amount: float
    metrics: Dict[str, Any]
    notes: Optional[str] = None

class IncentiveCreate(IncentiveBase):
    pass

class IncentiveUpdate(BaseModel):
    achieved_value: Optional[float] = None
    bonus_amount: Optional[float] = None
    total_amount: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    status: Optional[IncentiveStatus] = None

class Incentive(IncentiveBase):
    id: int
    status: IncentiveStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Incentive Payment Schemas
class IncentivePaymentBase(BaseModel):
    incentive_id: int
    amount: float
    payment_date: datetime
    payment_method: str
    payment_reference: str
    status: str
    notes: Optional[str] = None

class IncentivePaymentCreate(IncentivePaymentBase):
    pass

class IncentivePaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class IncentivePayment(IncentivePaymentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Response Schemas
class IncentiveResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class IncentiveSummary(BaseModel):
    total_incentives: int
    total_amount: float
    pending_incentives: int
    approved_incentives: int
    paid_incentives: int
    rejected_incentives: int
    by_type: Dict[str, int]
    by_period: Dict[str, int]
    recent_incentives: List[Incentive] 