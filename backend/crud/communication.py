from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.communication import MessageTemplate, Message, MessageStatus
from ..schemas.communication import MessageTemplateCreate, MessageTemplateUpdate, MessageCreate, MessageUpdate

def get_template(db: Session, template_id: int) -> Optional[MessageTemplate]:
    return db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()

def get_templates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    language: Optional[str] = None
) -> List[MessageTemplate]:
    query = db.query(MessageTemplate)
    if type:
        query = query.filter(MessageTemplate.type == type)
    if language:
        query = query.filter(MessageTemplate.language == language)
    return query.offset(skip).limit(limit).all()

def create_template(db: Session, template: MessageTemplateCreate, user_id: int) -> MessageTemplate:
    db_template = MessageTemplate(
        **template.dict(),
        created_by=user_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def update_template(
    db: Session,
    template_id: int,
    template: MessageTemplateUpdate
) -> Optional[MessageTemplate]:
    db_template = get_template(db, template_id)
    if db_template:
        update_data = template.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: int) -> bool:
    db_template = get_template(db, template_id)
    if db_template:
        db.delete(db_template)
        db.commit()
        return True
    return False

def get_message(db: Session, message_id: int) -> Optional[Message]:
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[MessageStatus] = None,
    sync_status: Optional[str] = None
) -> List[Message]:
    query = db.query(Message)
    if status:
        query = query.filter(Message.status == status)
    if sync_status:
        query = query.filter(Message.sync_status == sync_status)
    return query.offset(skip).limit(limit).all()

def create_message(db: Session, message: MessageCreate, user_id: int) -> Message:
    db_message = Message(
        **message.dict(),
        created_by=user_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(
    db: Session,
    message_id: int,
    message: MessageUpdate
) -> Optional[Message]:
    db_message = get_message(db, message_id)
    if db_message:
        update_data = message.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_message, field, value)
        db.commit()
        db.refresh(db_message)
    return db_message

def get_pending_messages(db: Session, limit: int = 100) -> List[Message]:
    return db.query(Message).filter(
        Message.status == MessageStatus.PENDING,
        Message.sync_status == "pending"
    ).limit(limit).all()

def mark_message_sent(db: Session, message_id: int) -> Optional[Message]:
    db_message = get_message(db, message_id)
    if db_message:
        db_message.status = MessageStatus.SENT
        db_message.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(db_message)
    return db_message

def mark_message_delivered(db: Session, message_id: int) -> Optional[Message]:
    db_message = get_message(db, message_id)
    if db_message:
        db_message.status = MessageStatus.DELIVERED
        db_message.delivered_at = datetime.utcnow()
        db.commit()
        db.refresh(db_message)
    return db_message

def mark_message_failed(db: Session, message_id: int, error_message: str) -> Optional[Message]:
    db_message = get_message(db, message_id)
    if db_message:
        db_message.status = MessageStatus.FAILED
        db_message.error_message = error_message
        db.commit()
        db.refresh(db_message)
    return db_message 