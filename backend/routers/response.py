from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..services.response import response_service
from ..services.notification import notification_service
from ..schemas.response import (
    ResponseCreate,
    ResponseUpdate,
    ResponseResponse,
    ResponseEscalationCreate,
    ResponseEscalationResponse,
    PatientResponseCreate, PatientResponseUpdate, PatientResponseResponse,
    ResponseFollowUpCreate, ResponseFollowUpUpdate, ResponseFollowUpResponse,
    ResponseTemplateCreate, ResponseTemplateUpdate, ResponseTemplateResponse,
    ResponseAnalyticsCreate, ResponseAnalyticsUpdate, ResponseAnalyticsResponse,
    ResponseStats
)
from ..auth import get_current_active_user
from ..models.user import User
from ..models.response import ResponseType, ResponseStatus, ResponseChannel

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/webhook/{provider}", status_code=200)
async def handle_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle webhooks from notification providers."""
    try:
        # Get webhook data
        data = await request.json()
        
        # Process based on provider
        if provider == "twilio":
            await _handle_twilio_webhook(db, data)
        elif provider == "africas_talking":
            await _handle_africas_talking_webhook(db, data)
        elif provider == "whatsapp":
            await _handle_whatsapp_webhook(db, data)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {provider}"
            )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

async def _handle_twilio_webhook(db: Session, data: Dict[str, Any]):
    """Handle Twilio webhook."""
    # Extract message details
    message_sid = data.get("MessageSid")
    from_number = data.get("From")
    body = data.get("Body")
    
    # Find associated notification
    notification = db.query(Notification).filter(
        Notification.metadata["message_sid"].astext == message_sid
    ).first()
    
    if notification:
        # Process response
        await response_service.process_response(
            db=db,
            notification_id=notification.id,
            patient_id=notification.patient_id,
            message=body,
            language=notification.patient.preferred_language
        )

async def _handle_africas_talking_webhook(db: Session, data: Dict[str, Any]):
    """Handle Africa's Talking webhook."""
    # Extract message details
    message_id = data.get("messageId")
    from_number = data.get("from")
    text = data.get("text")
    
    # Find associated notification
    notification = db.query(Notification).filter(
        Notification.metadata["message_id"].astext == message_id
    ).first()
    
    if notification:
        # Process response
        await response_service.process_response(
            db=db,
            notification_id=notification.id,
            patient_id=notification.patient_id,
            message=text,
            language=notification.patient.preferred_language
        )

async def _handle_whatsapp_webhook(db: Session, data: Dict[str, Any]):
    """Handle WhatsApp webhook."""
    # Extract message details
    message_id = data.get("message", {}).get("id")
    from_number = data.get("from")
    text = data.get("message", {}).get("text", {}).get("body")
    
    # Find associated notification
    notification = db.query(Notification).filter(
        Notification.metadata["message_id"].astext == message_id
    ).first()
    
    if notification:
        # Process response
        await response_service.process_response(
            db=db,
            notification_id=notification.id,
            patient_id=notification.patient_id,
            message=text,
            language=notification.patient.preferred_language
        )

@router.post("/", response_model=ResponseResponse)
async def create_response(
    response: ResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new response."""
    try:
        return await response_service.process_response(
            db=db,
            notification_id=response.notification_id,
            patient_id=response.patient_id,
            message=response.message,
            language=response.language
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/patient/{patient_id}", response_model=List[ResponseResponse])
async def get_patient_responses(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all responses for a patient."""
    return await response_service.get_patient_responses(
        db=db,
        patient_id=patient_id,
        skip=skip,
        limit=limit
    )

@router.get("/escalated", response_model=List[ResponseResponse])
async def get_escalated_responses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all escalated responses assigned to the current user."""
    return await response_service.get_escalated_responses(
        db=db,
        staff_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.post("/{response_id}/resolve", response_model=ResponseResponse)
async def resolve_response(
    response_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a response as resolved."""
    try:
        return await response_service.resolve_response(
            db=db,
            response_id=response_id,
            resolution_notes=resolution_notes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("", response_model=PatientResponseResponse)
async def create_patient_response(
    response: PatientResponseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new patient response."""
    try:
        return await response_service.create_patient_response(db, response.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{response_id}", response_model=PatientResponseResponse)
async def get_patient_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a patient response by ID."""
    response = await response_service.get_patient_response(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.put("/{response_id}", response_model=PatientResponseResponse)
async def update_patient_response(
    response_id: int,
    response_update: PatientResponseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a patient response."""
    response = await response_service.update_patient_response(
        db,
        response_id,
        response_update.dict(exclude_unset=True)
    )
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.get("", response_model=List[PatientResponseResponse])
async def get_patient_responses(
    reminder_id: Optional[int] = Query(None, description="Filter by reminder ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    response_type: Optional[ResponseType] = Query(None, description="Filter by response type"),
    channel: Optional[ResponseChannel] = Query(None, description="Filter by channel"),
    status: Optional[ResponseStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get patient responses with filters."""
    responses = await response_service.get_patient_responses(
        db,
        reminder_id=reminder_id,
        patient_id=patient_id,
        response_type=response_type,
        channel=channel,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return responses

@router.post("/{response_id}/process", response_model=List[ResponseFollowUpResponse])
async def process_response(
    response_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Process a patient response and create follow-up actions."""
    try:
        response, follow_ups = await response_service.process_response(db, response_id)
        return follow_ups
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow-ups", response_model=ResponseFollowUpResponse)
async def create_follow_up(
    follow_up: ResponseFollowUpCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new follow-up action."""
    try:
        return await response_service.create_follow_up(db, follow_up.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/follow-ups/{follow_up_id}", response_model=ResponseFollowUpResponse)
async def get_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a follow-up action by ID."""
    follow_up = await response_service.get_follow_up(db, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up

@router.put("/follow-ups/{follow_up_id}", response_model=ResponseFollowUpResponse)
async def update_follow_up(
    follow_up_id: int,
    follow_up_update: ResponseFollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a follow-up action."""
    follow_up = await response_service.update_follow_up(
        db,
        follow_up_id,
        follow_up_update.dict(exclude_unset=True)
    )
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up

@router.get("/follow-ups", response_model=List[ResponseFollowUpResponse])
async def get_pending_follow_ups(
    response_id: Optional[int] = Query(None, description="Filter by response ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get pending follow-up actions."""
    follow_ups = await response_service.get_pending_follow_ups(db, response_id)
    return follow_ups

@router.post("/templates", response_model=ResponseTemplateResponse)
async def create_template(
    template: ResponseTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new response template."""
    try:
        return await response_service.create_template(db, template.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=ResponseTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a template by ID."""
    template = await response_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=ResponseTemplateResponse)
async def update_template(
    template_id: int,
    template_update: ResponseTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a template."""
    template = await response_service.update_template(
        db,
        template_id,
        template_update.dict(exclude_unset=True)
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/stats", response_model=ResponseStats)
async def get_response_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get comprehensive response statistics."""
    try:
        return await response_service.get_response_stats(
            db,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 