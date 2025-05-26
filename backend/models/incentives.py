from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base

class RewardType(str, enum.Enum):
    MONETARY = "monetary"
    POINTS = "points"
    BADGE = "badge"
    CERTIFICATE = "certificate"
    OTHER = "other"

class AchievementType(str, enum.Enum):
    VISIT_COUNT = "visit_count"
    PATIENT_COUNT = "patient_count"
    ADHERENCE_RATE = "adherence_rate"
    QUALITY_SCORE = "quality_score"
    TRAINING_COMPLETION = "training_completion"
    REFERRAL_COUNT = "referral_count"
    OTHER = "other"

class AdherenceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

class Reward(Base):
    """Model for tracking rewards and incentives"""
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_type = Column(Enum(RewardType), nullable=False)
    amount = Column(Float)  # For monetary rewards or points
    description = Column(String)
    status = Column(String, default="pending")  # pending, approved, distributed
    distribution_date = Column(DateTime)
    metadata = Column(JSON)  # Additional reward details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("User", back_populates="rewards")

class Achievement(Base):
    """Model for tracking CHW achievements"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_type = Column(Enum(AchievementType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    criteria = Column(JSON)  # Achievement criteria
    progress = Column(Float, default=0.0)  # Progress towards achievement
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    metadata = Column(JSON)  # Additional achievement details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("User", back_populates="achievements")

class AdherenceTracking(Base):
    """Model for tracking patient adherence to treatment plans"""
    __tablename__ = "adherence_tracking"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id"), nullable=False)
    status = Column(Enum(AdherenceStatus), default=AdherenceStatus.UNKNOWN)
    adherence_rate = Column(Float)  # Percentage of adherence
    last_check_date = Column(DateTime)
    next_check_date = Column(DateTime)
    notes = Column(String)
    metadata = Column(JSON)  # Additional adherence details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="adherence_records")
    chw = relationship("User", back_populates="adherence_tracking")
    treatment_plan = relationship("TreatmentPlan", back_populates="adherence_records")

class AdherenceCheck(Base):
    """Model for individual adherence checks"""
    __tablename__ = "adherence_checks"

    id = Column(Integer, primary_key=True, index=True)
    adherence_id = Column(Integer, ForeignKey("adherence_tracking.id"), nullable=False)
    check_date = Column(DateTime, nullable=False)
    is_compliant = Column(Boolean)
    notes = Column(String)
    evidence = Column(JSON)  # Photos, documents, or other evidence
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    adherence = relationship("AdherenceTracking", back_populates="checks")

class IncentiveProgram(Base):
    """Model for managing incentive programs"""
    __tablename__ = "incentive_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    criteria = Column(JSON)  # Program criteria and rules
    rewards = Column(JSON)  # Available rewards
    metadata = Column(JSON)  # Additional program details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProgramEnrollment(Base):
    """Model for tracking CHW enrollment in incentive programs"""
    __tablename__ = "program_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("incentive_programs.id"), nullable=False)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    enrollment_date = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active, completed, withdrawn
    progress = Column(Float, default=0.0)
    rewards_earned = Column(JSON)  # List of earned rewards
    metadata = Column(JSON)  # Additional enrollment details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("IncentiveProgram")
    chw = relationship("User", back_populates="program_enrollments")

class IncentiveType(str, enum.Enum):
    PERFORMANCE = "performance"
    ATTENDANCE = "attendance"
    PATIENT_SATISFACTION = "patient_satisfaction"
    QUALITY_CARE = "quality_care"
    SPECIAL_ACHIEVEMENT = "special_achievement"

class IncentiveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"

class IncentivePeriod(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class Incentive(Base):
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    incentive_type = Column(Enum(IncentiveType))
    period = Column(Enum(IncentivePeriod))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    target_value = Column(Float)
    achieved_value = Column(Float)
    base_amount = Column(Float)
    bonus_amount = Column(Float)
    total_amount = Column(Float)
    status = Column(Enum(IncentiveStatus), default=IncentiveStatus.PENDING)
    metrics = Column(JSON)  # Store detailed metrics that contributed to the incentive
    notes = Column(String, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    payment_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility = relationship("Facility", back_populates="incentives")
    user = relationship("User", foreign_keys=[user_id], back_populates="earned_incentives")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_incentives")

class IncentiveRule(Base):
    __tablename__ = "incentive_rules"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    incentive_type = Column(Enum(IncentiveType))
    period = Column(Enum(IncentivePeriod))
    name = Column(String)
    description = Column(String)
    target_metric = Column(String)  # e.g., "patient_satisfaction_score", "appointment_completion_rate"
    target_value = Column(Float)
    base_amount = Column(Float)
    bonus_multiplier = Column(Float)  # Multiplier for exceeding target
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility = relationship("Facility", back_populates="incentive_rules")

class IncentivePayment(Base):
    __tablename__ = "incentive_payments"

    id = Column(Integer, primary_key=True, index=True)
    incentive_id = Column(Integer, ForeignKey("incentives.id"))
    amount = Column(Float)
    payment_date = Column(DateTime)
    payment_method = Column(String)  # e.g., "bank_transfer", "mobile_money", "cash"
    payment_reference = Column(String)
    status = Column(String)  # e.g., "pending", "completed", "failed"
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incentive = relationship("Incentive", back_populates="payments")

# Add relationships to existing models
from .user import User
User.earned_incentives = relationship("Incentive", foreign_keys="[Incentive.user_id]", back_populates="user")
User.approved_incentives = relationship("Incentive", foreign_keys="[Incentive.approved_by]", back_populates="approver")

from .facility import Facility
Facility.incentives = relationship("Incentive", back_populates="facility")
Facility.incentive_rules = relationship("IncentiveRule", back_populates="facility") 