from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class MessageType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"

class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(Enum(MessageType), nullable=False)
    language = Column(String, nullable=False)
    variables = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    creator = relationship("User", back_populates="templates")
    messages = relationship("Message", back_populates="template")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("message_templates.id"))
    recipient = Column(String, nullable=False)
    variables = Column(JSON, nullable=False, default=dict)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    sync_status = Column(String, default="pending")  # For offline sync

    template = relationship("MessageTemplate", back_populates="messages")
    creator = relationship("User", back_populates="messages") 