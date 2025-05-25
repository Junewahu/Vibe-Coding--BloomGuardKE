from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models.caregiver import CommunicationChannel
from ..services.caregiver import caregiver_service
from ..schemas.caregiver import (
    CaregiverCreate,
    CaregiverUpdate,
    CaregiverResponse,
    CommunicationCreate,
    CommunicationResponse,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    EngagementCreate,
    EngagementResponse,
    BroadcastMessage,
    VoiceNoteContent,
    EngagementStats
)

router = APIRouter(prefix="/caregivers", tags=["caregivers"])

@router.post("/", response_model=CaregiverResponse)
async def create_caregiver(
    caregiver: CaregiverCreate,
    db: Session = Depends(get_db)
):
    """Create a new caregiver."""
    try:
        return await caregiver_service.create_caregiver(db, caregiver.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{caregiver_id}", response_model=CaregiverResponse)
async def get_caregiver(
    caregiver_id: int,
    db: Session = Depends(get_db)
):
    """Get a caregiver by ID."""
    caregiver = await caregiver_service.get_caregiver(db, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return caregiver

@router.put("/{caregiver_id}", response_model=CaregiverResponse)
async def update_caregiver(
    caregiver_id: int,
    caregiver_update: CaregiverUpdate,
    db: Session = Depends(get_db)
):
    """Update a caregiver's information."""
    caregiver = await caregiver_service.update_caregiver(
        db,
        caregiver_id,
        caregiver_update.dict(exclude_unset=True)
    )
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return caregiver

@router.post("/{caregiver_id}/communicate", response_model=CommunicationResponse)
async def send_communication(
    caregiver_id: int,
    communication: CommunicationCreate,
    db: Session = Depends(get_db)
):
    """Send a communication to a caregiver."""
    try:
        return await caregiver_service.send_communication(
            db=db,
            caregiver_id=caregiver_id,
            template_name=communication.template_name,
            variables=communication.content,
            channel=communication.channel,
            metadata=communication.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast", response_model=List[CommunicationResponse])
async def broadcast_message(
    broadcast: BroadcastMessage,
    db: Session = Depends(get_db)
):
    """Broadcast a message to multiple caregivers."""
    try:
        return await caregiver_service.broadcast_message(
            db=db,
            template_name=broadcast.template_name,
            caregiver_ids=broadcast.caregiver_ids,
            variables=broadcast.variables,
            channel=broadcast.channel,
            schedule_time=broadcast.schedule_time,
            metadata=broadcast.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{caregiver_id}/voice-note", response_model=CommunicationResponse)
async def handle_voice_note(
    caregiver_id: int,
    audio_file: UploadFile = File(...),
    duration: int = Query(..., description="Duration of the voice note in seconds"),
    language: str = Query("en", description="Language of the voice note"),
    db: Session = Depends(get_db)
):
    """Handle an incoming voice note from a caregiver."""
    try:
        audio_content = await audio_file.read()
        communication, transcription = await caregiver_service.handle_voice_note(
            db=db,
            caregiver_id=caregiver_id,
            audio_file=audio_content,
            duration=duration,
            language=language
        )
        return communication
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{caregiver_id}/engagement", response_model=EngagementResponse)
async def track_engagement(
    caregiver_id: int,
    engagement: EngagementCreate,
    db: Session = Depends(get_db)
):
    """Track caregiver engagement."""
    try:
        return await caregiver_service.track_engagement(
            db=db,
            caregiver_id=caregiver_id,
            engagement_type=engagement.engagement_type,
            interaction_data=engagement.interaction_data,
            response_time=engagement.response_time,
            notes=engagement.notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{caregiver_id}/engagement/stats", response_model=EngagementStats)
async def get_engagement_stats(
    caregiver_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: Session = Depends(get_db)
):
    """Get engagement statistics for a caregiver."""
    try:
        return await caregiver_service.get_engagement_stats(
            db=db,
            caregiver_id=caregiver_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new communication template."""
    try:
        template_model = CommunicationTemplate(**template.dict())
        db.add(template_model)
        db.commit()
        db.refresh(template_model)
        return template_model
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update a communication template."""
    template = db.query(CommunicationTemplate).filter(
        CommunicationTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for key, value in template_update.dict(exclude_unset=True).items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template

@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    channel: Optional[CommunicationChannel] = Query(None, description="Filter by channel"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """List communication templates."""
    query = db.query(CommunicationTemplate)
    
    if channel:
        query = query.filter(CommunicationTemplate.channel == channel)
    if language:
        query = query.filter(CommunicationTemplate.language == language)
    if is_active is not None:
        query = query.filter(CommunicationTemplate.is_active == is_active)
    
    return query.all() 