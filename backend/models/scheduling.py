from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class ScheduleType(str, enum.Enum):
    IMMUNIZATION = "immunization"
    MILESTONE = "milestone"
    POST_OPERATIVE = "post_operative"
    CHRONIC_CARE = "chronic_care"
    CUSTOM = "custom"

class ScheduleStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class ScheduleRule(Base):
    """Model for storing schedule rules"""
    __tablename__ = "schedule_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_type = Column(Enum(ScheduleType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    conditions = Column(JSON)  # Rule conditions
    schedule_template = Column(JSON)  # Schedule template
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="schedule_rules")

class CustomProtocol(Base):
    """Model for storing custom protocols"""
    __tablename__ = "custom_protocols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    protocol_type = Column(String)  # Type of protocol
    steps = Column(JSON)  # Protocol steps
    duration = Column(Integer)  # Duration in days
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="custom_protocols")

class FollowUpSchedule(Base):
    """Model for storing follow-up schedules"""
    __tablename__ = "follow_up_schedules"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    schedule_type = Column(Enum(ScheduleType), nullable=False)
    rule_id = Column(Integer, ForeignKey("schedule_rules.id"))
    protocol_id = Column(Integer, ForeignKey("custom_protocols.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PENDING)
    visits = Column(JSON)  # Scheduled visits
    adjustments = Column(JSON)  # Schedule adjustments
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="follow_up_schedules")
    rule = relationship("ScheduleRule")
    protocol = relationship("CustomProtocol")
    creator = relationship("User", back_populates="created_schedules")

class ScheduleAdjustment(Base):
    """Model for storing schedule adjustments"""
    __tablename__ = "schedule_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("follow_up_schedules.id"), nullable=False)
    reason = Column(String, nullable=False)
    original_date = Column(DateTime, nullable=False)
    new_date = Column(DateTime, nullable=False)
    adjustment_type = Column(String)  # reschedule, cancel, etc.
    notes = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedule = relationship("FollowUpSchedule", back_populates="adjustments")
    creator = relationship("User", back_populates="schedule_adjustments")

# Add relationships to User model
from .user import User
User.schedule_rules = relationship("ScheduleRule", back_populates="creator")
User.custom_protocols = relationship("CustomProtocol", back_populates="creator")
User.created_schedules = relationship("FollowUpSchedule", back_populates="creator")
User.schedule_adjustments = relationship("ScheduleAdjustment", back_populates="creator") 