from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class NotificationType(str, enum.Enum):
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    ALERT = "alert"
    UPDATE = "update"
    SYSTEM = "system"
    CUSTOM = "custom"

class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    USSD = "ussd"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RESPONDED = "responded"

class NotificationTemplate(Base):
    """Model for notification templates"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    subject = Column(String(200), nullable=True)  # For email notifications
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Template variables
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    """Model for notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    subject = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate")

class NotificationPreference(Base):
    """Model for user notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_enabled = Column(Boolean, default=True)
    priority_threshold = Column(Enum(NotificationPriority), default=NotificationPriority.LOW)
    quiet_hours_start = Column(DateTime, nullable=True)
    quiet_hours_end = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class NotificationDelivery(Base):
    """Model for tracking notification delivery attempts"""
    __tablename__ = "notification_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    next_attempt_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notification = relationship("Notification", back_populates="deliveries")

class WhatsAppSession(Base):
    """Model for storing WhatsApp sessions"""
    __tablename__ = "whatsapp_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    status = Column(String)  # active, inactive, blocked
    last_interaction = Column(DateTime)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="whatsapp_sessions")

class VoiceCall(Base):
    """Model for storing voice calls"""
    __tablename__ = "voice_calls"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    call_id = Column(String, nullable=False)
    status = Column(String)  # initiated, in-progress, completed, failed
    duration = Column(Integer)  # Duration in seconds
    recording_url = Column(String)
    transcription = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="voice_calls")

class USSDMenu(Base):
    """Model for storing USSD menus"""
    __tablename__ = "ussd_menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    menu_text = Column(Text, nullable=False)
    options = Column(JSON)  # Menu options and their actions
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="ussd_menus")

class USSDSession(Base):
    """Model for storing USSD sessions"""
    __tablename__ = "ussd_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    menu_id = Column(Integer, ForeignKey("ussd_menus.id"))
    current_state = Column(String)
    input_history = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="ussd_sessions")
    menu = relationship("USSDMenu")

# Add relationships to Patient model
from .patient import Patient
Patient.notifications = relationship("Notification", back_populates="patient")
Patient.whatsapp_sessions = relationship("WhatsAppSession", back_populates="patient")
Patient.voice_calls = relationship("VoiceCall", back_populates="patient")
Patient.ussd_sessions = relationship("USSDSession", back_populates="patient")

# Add relationships to User model
from .user import User
User.notification_templates = relationship("NotificationTemplate", back_populates="creator")
User.ussd_menus = relationship("USSDMenu", back_populates="creator") 