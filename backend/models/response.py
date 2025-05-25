from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class ResponseType(str, enum.Enum):
    CONFIRM = "confirm"
    RESCHEDULE = "reschedule"
    CANCEL = "cancel"
    DECLINE = "decline"
    NO_RESPONSE = "no_response"
    ERROR = "error"

class ResponseChannel(str, enum.Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    USSD = "ussd"
    EMAIL = "email"
    PUSH = "push"
    WEB = "web"
    MOBILE = "mobile"

class ResponseStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALID = "invalid"

class PatientResponse(Base):
    """Model for patient responses to reminders"""
    __tablename__ = "patient_responses"

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    response_type = Column(Enum(ResponseType), nullable=False)
    response_channel = Column(Enum(ResponseChannel), nullable=False)
    status = Column(Enum(ResponseStatus), default=ResponseStatus.RECEIVED)
    content = Column(Text, nullable=True)
    response_data = Column(JSON, nullable=True)
    response_time = Column(DateTime, nullable=False)
    processed_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reminder = relationship("Reminder", back_populates="patient_responses")
    patient = relationship("Patient", back_populates="responses")
    follow_up_actions = relationship("ResponseFollowUp", back_populates="response")

class ResponseFollowUp(Base):
    """Model for follow-up actions based on responses"""
    __tablename__ = "response_follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("patient_responses.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # reschedule, notify_staff, etc.
    status = Column(String(50), nullable=False)  # pending, completed, failed
    action_data = Column(JSON, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    completed_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    response = relationship("PatientResponse", back_populates="follow_up_actions")

class ResponseTemplate(Base):
    """Model for response templates"""
    __tablename__ = "response_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    response_type = Column(Enum(ResponseType), nullable=False)
    channel = Column(Enum(ResponseChannel), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)
    language = Column(String(10), default="en")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResponseAnalytics(Base):
    """Model for response analytics"""
    __tablename__ = "response_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    response_type = Column(Enum(ResponseType), nullable=False)
    channel = Column(Enum(ResponseChannel), nullable=False)
    count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_response_time = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Add unique constraint for date, response_type, and channel combination
        # This ensures we have one record per type/channel per day
        {'sqlite_autoincrement': True},
    ) 