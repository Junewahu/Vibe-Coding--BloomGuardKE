from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class EventType(str, enum.Enum):
    SCHEDULE = "schedule"
    APPOINTMENT = "appointment"
    FOLLOW_UP = "follow_up"
    CUSTOM = "custom"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)
    location = Column(String(200), nullable=True)
    color = Column(String(20), nullable=True)  # For UI color coding
    metadata = Column(JSON, nullable=True)  # Additional event data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys (optional, depending on event type)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    follow_up_id = Column(Integer, ForeignKey("follow_up_schedules.id"), nullable=True)

    # Relationships
    schedule = relationship("Schedule", back_populates="calendar_events")
    appointment = relationship("Appointment", back_populates="calendar_events")
    follow_up = relationship("FollowUpSchedule", back_populates="calendar_events")

    def __repr__(self):
        return f"<CalendarEvent {self.id} - {self.title}>" 