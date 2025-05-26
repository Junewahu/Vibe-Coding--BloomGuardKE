from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"

class MessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class MessageTemplateBase(BaseModel):
    name: str
    content: str
    type: MessageType
    language: str
    variables: List[str] = Field(default_factory=list)

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(MessageTemplateBase):
    is_active: Optional[bool] = None

class MessageTemplate(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    is_active: bool

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    template_id: int
    recipient: str
    variables: Dict[str, str] = Field(default_factory=dict)

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    status: Optional[MessageStatus] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    sync_status: Optional[str] = None

class Message(MessageBase):
    id: int
    status: MessageStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: int
    sync_status: str

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    success: bool
    message_id: Optional[int] = None
    error: Optional[str] = None 