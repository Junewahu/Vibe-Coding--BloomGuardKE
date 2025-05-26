from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..auth import get_current_user
from ..schemas.communication import (
    MessageTemplate,
    MessageTemplateCreate,
    MessageTemplateUpdate,
    Message,
    MessageCreate,
    MessageResponse
)
from ..crud import communication as crud
from ..services.communication import communication_service
from ..models.user import User

router = APIRouter(prefix="/communications", tags=["communications"])

@router.get("/templates", response_model=List[MessageTemplate])
async def get_templates(
    type: Optional[str] = None,
    language: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = crud.get_templates(db, skip=skip, limit=limit, type=type, language=language)
    return templates

@router.post("/templates", response_model=MessageTemplate)
async def create_template(
    template: MessageTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_template(db, template, current_user.id)

@router.put("/templates/{template_id}", response_model=MessageTemplate)
async def update_template(
    template_id: int,
    template: MessageTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_template = crud.get_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    if db_template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    return crud.update_template(db, template_id, template)

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_template = crud.get_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    if db_template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    if crud.delete_template(db, template_id):
        return {"message": "Template deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete template")

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create message record
    db_message = crud.create_message(db, message, current_user.id)
    
    # Send message in background
    async def send_message_task():
        result = await communication_service.send_message(db_message)
        if result["success"]:
            crud.mark_message_sent(db, db_message.id)
        else:
            crud.mark_message_failed(db, db_message.id, result["error"])
    
    background_tasks.add_task(send_message_task)
    
    return {
        "success": True,
        "message_id": db_message.id
    }

@router.get("/status/{message_id}", response_model=Message)
async def get_message_status(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = crud.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this message")
    return message

@router.get("/messages", response_model=List[Message])
async def get_messages(
    status: Optional[str] = None,
    sync_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = crud.get_messages(
        db,
        skip=skip,
        limit=limit,
        status=status,
        sync_status=sync_status
    )
    return messages 