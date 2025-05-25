from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base

class FollowUpType(str, enum.Enum):
    ROUTINE = "routine"
    POST_TREATMENT = "post_treatment"
    MEDICATION_REVIEW = "medication_review"
    TEST_RESULTS = "test_results"
    SPECIALIST_CONSULTATION = "specialist_consultation"

class FollowUpStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class FollowUpSchedule(Base):
    __tablename__ = "follow_up_schedules"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    
    # Follow-up details
    follow_up_type = Column(Enum(FollowUpType))
    status = Column(Enum(FollowUpStatus), default=FollowUpStatus.SCHEDULED)
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    # Recurrence settings
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)  # Store recurrence rules
    end_date = Column(DateTime, nullable=True)
    
    # Additional information
    notes = Column(String(500))
    priority = Column(Integer, default=1)  # 1-5, where 5 is highest
    reminder_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="follow_ups")
    doctor = relationship("User", back_populates="follow_ups")
    appointments = relationship("Appointment", back_populates="follow_up") 