from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.reminder import ReminderChannel, ReminderStatus, ReminderPriority
from ..services.reminder import reminder_service
from ..schemas.reminder import (
    ReminderCreate, ReminderUpdate, ReminderResponse,
    ReminderResponseCreate, ReminderResponseUpdate, ReminderResponseResponse,
    ReminderTemplateCreate, ReminderTemplateUpdate, ReminderTemplateResponse,
    ReminderDeliveryLogCreate, ReminderDeliveryLogUpdate, ReminderDeliveryLogResponse,
    ReminderProviderCreate, ReminderProviderUpdate, ReminderProviderResponse,
    ReminderStats
)
from .. import auth

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("", response_model=ReminderResponse)
async def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a new reminder."""
    try:
        return await reminder_service.create_reminder(db, reminder.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get a reminder by ID."""
    reminder = await reminder_service.get_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Update a reminder."""
    reminder = await reminder_service.update_reminder(
        db,
        reminder_id,
        reminder_update.dict(exclude_unset=True)
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.get("", response_model=List[ReminderResponse])
async def get_reminders(
    schedule_id: Optional[int] = Query(None, description="Filter by schedule ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[ReminderStatus] = Query(None, description="Filter by status"),
    channel: Optional[ReminderChannel] = Query(None, description="Filter by channel"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get reminders with filters."""
    reminders = await reminder_service.get_reminders(
        db,
        schedule_id=schedule_id,
        patient_id=patient_id,
        status=status,
        channel=channel,
        start_date=start_date,
        end_date=end_date
    )
    return reminders

@router.post("/{reminder_id}/responses", response_model=ReminderResponseResponse)
async def create_reminder_response(
    reminder_id: int,
    response: ReminderResponseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a reminder response."""
    try:
        return await reminder_service.create_reminder_response(
            db,
            reminder_id,
            response.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/templates", response_model=ReminderTemplateResponse)
async def create_template(
    template: ReminderTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a new reminder template."""
    try:
        return await reminder_service.create_template(db, template.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=ReminderTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get a template by ID."""
    template = await reminder_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=ReminderTemplateResponse)
async def update_template(
    template_id: int,
    template_update: ReminderTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Update a template."""
    template = await reminder_service.update_template(
        db,
        template_id,
        template_update.dict(exclude_unset=True)
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/providers", response_model=ReminderProviderResponse)
async def create_provider(
    provider: ReminderProviderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a new reminder provider."""
    try:
        return await reminder_service.create_provider(db, provider.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/providers/{provider_id}", response_model=ReminderProviderResponse)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get a provider by ID."""
    provider = await reminder_service.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.put("/providers/{provider_id}", response_model=ReminderProviderResponse)
async def update_provider(
    provider_id: int,
    provider_update: ReminderProviderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Update a provider."""
    provider = await reminder_service.update_provider(
        db,
        provider_id,
        provider_update.dict(exclude_unset=True)
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.post("/process", response_model=List[ReminderResponse])
async def process_pending_reminders(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Process pending reminders."""
    try:
        results = await reminder_service.process_pending_reminders(db)
        return [reminder for reminder, success in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ReminderStats)
async def get_reminder_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get comprehensive reminder statistics."""
    try:
        return await reminder_service.get_reminder_stats(
            db,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 