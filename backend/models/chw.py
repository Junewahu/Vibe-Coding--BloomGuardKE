from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class VisitStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

class VisitType(str, enum.Enum):
    ROUTINE = "routine"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ASSESSMENT = "assessment"
    EDUCATION = "education"

class CHWStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"

class CHW(Base, BaseModel):
    """Model for Community Health Worker information"""
    __tablename__ = "chws"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(100), nullable=True)
    status = Column(Enum(CHWStatus), default=CHWStatus.ACTIVE)
    assigned_area = Column(String(200))  # Geographic area of responsibility
    qualifications = Column(JSON)  # List of qualifications and certifications
    training_history = Column(JSON)  # Training records
    performance_metrics = Column(JSON)  # Performance tracking data
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chw_profile")
    visits = relationship("CHWVisit", back_populates="chw")
    assignments = relationship("CHWAssignment", back_populates="chw")

    def __repr__(self):
        return f"<CHW {self.first_name} {self.last_name}>"

class CHWVisit(Base):
    """Model for tracking CHW field visits"""
    __tablename__ = "chw_visits"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("chws.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_type = Column(Enum(VisitType))
    status = Column(Enum(VisitStatus), default=VisitStatus.SCHEDULED)
    scheduled_date = Column(DateTime)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    location = Column(JSON)  # GPS coordinates and address
    findings = Column(JSON)  # Visit findings and observations
    recommendations = Column(JSON)  # Recommendations and follow-up actions
    photos = Column(JSON, nullable=True)  # URLs to visit photos
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("CHW", back_populates="visits")
    patient = relationship("Patient")

class CHWAssignment(Base):
    """Model for tracking CHW assignments"""
    __tablename__ = "chw_assignments"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("chws.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    assignment_type = Column(String(50))  # e.g., "primary", "backup", "temporary"
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("CHW", back_populates="assignments")
    patient = relationship("Patient")

class CHWPerformance(Base):
    """Model for tracking CHW performance metrics"""
    __tablename__ = "chw_performance"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("chws.id"))
    metric_date = Column(DateTime)
    visits_completed = Column(Integer, default=0)
    patients_served = Column(Integer, default=0)
    follow_ups_completed = Column(Integer, default=0)
    emergency_visits = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)  # in minutes
    patient_satisfaction = Column(Float, nullable=True)  # 0-5 scale
    compliance_rate = Column(Float, nullable=True)  # percentage
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("CHW")

class CHWTraining(Base):
    """Model for tracking CHW training and certifications"""
    __tablename__ = "chw_training"

    id = Column(Integer, primary_key=True, index=True)
    chw_id = Column(Integer, ForeignKey("chws.id"))
    training_name = Column(String(200))
    training_type = Column(String(100))
    provider = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20))  # e.g., "completed", "in_progress", "scheduled"
    certification_id = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chw = relationship("CHW") 