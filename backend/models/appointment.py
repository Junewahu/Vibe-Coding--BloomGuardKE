from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import BaseModel
from ..database import Base

class AppointmentType(enum.Enum):
    VACCINATION = "vaccination"
    CHECKUP = "checkup"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    OTHER = "other"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class Appointment(Base, BaseModel):
    """Appointment model for scheduling and tracking patient visits"""
    
    # Basic Information
    patient_id = Column(ForeignKey("patient.id"), nullable=False)
    doctor_id = Column(ForeignKey("user.id"), nullable=False)
    appointment_type = Column(Enum(AppointmentType), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    notes = Column(String(500))
    
    # Reminder Settings
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)
    reminder_preferences = Column(JSON)  # Store preferred contact methods and times
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(String(500))
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="appointments")
    reminders = relationship("Reminder", back_populates="appointment")
    
    def __repr__(self):
        return f"<Appointment {self.id} - {self.appointment_type.value}>"
    
    @property
    def is_past(self):
        return self.scheduled_at < datetime.utcnow()
    
    @property
    def is_upcoming(self):
        return self.scheduled_at > datetime.utcnow() and self.status == AppointmentStatus.SCHEDULED
    
    def to_dict(self):
        data = super().to_dict()
        data["appointment_type"] = self.appointment_type.value
        data["status"] = self.status.value
        return data 