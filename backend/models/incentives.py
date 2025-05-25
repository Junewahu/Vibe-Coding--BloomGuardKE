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