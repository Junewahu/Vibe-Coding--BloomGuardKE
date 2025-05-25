from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class ReminderChannel(str, enum.Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    USSD = "ussd"
    EMAIL = "email"
    PUSH = "push"

class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReminderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Reminder(Base):
    """Model for reminders"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    channel = Column(Enum(ReminderChannel), nullable=False)
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING)
    priority = Column(Enum(ReminderPriority), default=ReminderPriority.MEDIUM)
    content = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    sent_time = Column(DateTime, nullable=True)
    delivered_time = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedule = relationship("Schedule", back_populates="reminders")
    patient = relationship("Patient", back_populates="reminders")
    responses = relationship("ReminderResponse", back_populates="reminder")
    delivery_logs = relationship("ReminderDeliveryLog", back_populates="reminder")
    template = relationship("ReminderTemplate", back_populates="reminders")

class ReminderResponse(Base):
    """Model for reminder responses"""
    __tablename__ = "reminder_responses"

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    response_type = Column(String(50), nullable=False)  # confirm, reschedule, cancel, etc.
    response_data = Column(JSON, nullable=True)
    response_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reminder = relationship("Reminder", back_populates="responses")

class ReminderTemplate(Base):
    """Model for reminder templates"""
    __tablename__ = "reminder_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    channel = Column(Enum(ReminderChannel), nullable=False)
    content_type = Column(String(50), nullable=False)  # text, html, audio, etc.
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Template variables
    language = Column(String(10), default="en")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reminders = relationship("Reminder", back_populates="template")

class ReminderDeliveryLog(Base):
    """Model for reminder delivery logs"""
    __tablename__ = "reminder_delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    channel = Column(Enum(ReminderChannel), nullable=False)
    status = Column(Enum(ReminderStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    provider_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reminder = relationship("Reminder", back_populates="delivery_logs")

class ReminderProvider(Base):
    """Model for reminder service providers"""
    __tablename__ = "reminder_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    channel = Column(Enum(ReminderChannel), nullable=False)
    api_key = Column(String(200), nullable=False)
    api_secret = Column(String(200), nullable=False)
    configuration = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ReminderProvider {self.id} - {self.name}>"

    @property
    def is_deliverable(self):
        return self.active

    def to_dict(self):
        data = super().to_dict()
        data["channel"] = self.channel.value
        return data 