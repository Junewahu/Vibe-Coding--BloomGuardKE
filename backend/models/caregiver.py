from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class CaregiverType(str, enum.Enum):
    FAMILY = "family"
    PROFESSIONAL = "professional"
    VOLUNTEER = "volunteer"

class CommunicationChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    SMS = "sms"
    EMAIL = "email"

class CommunicationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Caregiver(Base, BaseModel):
    """Model for caregiver information"""
    __tablename__ = "caregivers"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(Enum(CaregiverType))
    relationship = Column(String(100))  # e.g., "spouse", "child", "nurse"
    name = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False)
    preferred_language = Column(String(10), default="en")
    preferred_channel = Column(Enum(CommunicationChannel), default=CommunicationChannel.WHATSAPP)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="caregivers")
    user = relationship("User", back_populates="caregiver_profile")
    communications = relationship("CaregiverCommunication", back_populates="caregiver")

    def __repr__(self):
        return f"<Caregiver {self.name}>"
    
    @property
    def full_name(self):
        return self.name

class CaregiverCommunication(Base):
    """Model for tracking communications with caregivers"""
    __tablename__ = "caregiver_communications"

    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id"))
    channel = Column(Enum(CommunicationChannel))
    template_name = Column(String(100))
    content = Column(JSON)  # Stores message content, media URLs, etc.
    status = Column(Enum(CommunicationStatus), default=CommunicationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional communication metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    caregiver = relationship("Caregiver", back_populates="communications")

class CommunicationTemplate(Base):
    """Model for storing communication templates"""
    __tablename__ = "communication_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    channel = Column(Enum(CommunicationChannel))
    content_type = Column(String(50))  # e.g., "text", "voice", "media"
    content = Column(JSON)  # Template content with variables
    variables = Column(JSON)  # List of required variables
    language = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaregiverEngagement(Base):
    """Model for tracking caregiver engagement"""
    __tablename__ = "caregiver_engagement"

    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id"))
    engagement_type = Column(String(50))  # e.g., "message_response", "appointment_reminder"
    engagement_date = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Integer, nullable=True)  # Response time in seconds
    interaction_data = Column(JSON)  # Details about the interaction
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    caregiver = relationship("Caregiver")

    def to_dict(self):
        data = super().to_dict()
        data["engagement_type"] = self.engagement_type
        data["engagement_date"] = self.engagement_date
        data["response_time"] = self.response_time
        data["interaction_data"] = self.interaction_data
        data["notes"] = self.notes
        return data 