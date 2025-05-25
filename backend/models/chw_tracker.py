from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base

class VisitStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class ActivityType(str, enum.Enum):
    HOME_VISIT = "home_visit"
    FOLLOW_UP = "follow_up"
    VACCINATION = "vaccination"
    HEALTH_EDUCATION = "health_education"
    REFERRAL = "referral"
    DATA_COLLECTION = "data_collection"
    OTHER = "other"

class CHWFieldVisit(Base):
    """Model for tracking CHW field visits"""
    __tablename__ = "chw_field_visits"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    status = Column(Enum(VisitStatus), default=VisitStatus.SCHEDULED)
    visit_type = Column(Enum(ActivityType), nullable=False)
    notes = Column(String)
    location = Column(JSON)  # Stores latitude, longitude, and address
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("User", back_populates="field_visits")
    patient = relationship("Patient", back_populates="chw_visits")
    activities = relationship("CHWActivity", back_populates="visit")
    location_tracking = relationship("CHWLocationTracking", back_populates="visit")

class CHWActivity(Base):
    """Model for tracking specific activities during field visits"""
    __tablename__ = "chw_activities"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("chw_field_visits.id"), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    outcome = Column(String)
    metrics = Column(JSON)  # Stores activity-specific metrics
    photos = Column(JSON)  # Stores photo URLs or metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    visit = relationship("CHWFieldVisit", back_populates="activities")

class CHWLocationTracking(Base):
    """Model for tracking CHW location during field visits"""
    __tablename__ = "chw_location_tracking"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("chw_field_visits.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    accuracy = Column(Float)  # GPS accuracy in meters
    speed = Column(Float)  # Speed in meters per second
    heading = Column(Float)  # Direction in degrees
    altitude = Column(Float)  # Altitude in meters
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    visit = relationship("CHWFieldVisit", back_populates="location_tracking")

class CHWPerformanceMetrics(Base):
    """Model for tracking CHW performance metrics"""
    __tablename__ = "chw_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    total_visits = Column(Integer, default=0)
    completed_visits = Column(Integer, default=0)
    cancelled_visits = Column(Integer, default=0)
    no_shows = Column(Integer, default=0)
    total_distance = Column(Float, default=0.0)  # Total distance traveled in kilometers
    average_visit_duration = Column(Float)  # Average duration in minutes
    metrics = Column(JSON)  # Additional performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("User", back_populates="performance_metrics") 