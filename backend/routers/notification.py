from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user, get_current_user
from ..models.user import User
from ..services.notification import notification_service, NotificationService
from ..schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    NotificationPreferenceCreate, NotificationPreferenceUpdate, NotificationPreferenceResponse,
    NotificationLogResponse, NotificationStats,
    WhatsAppSessionCreate, WhatsAppSessionUpdate, WhatsAppSessionResponse,
    VoiceCallCreate, VoiceCallUpdate, VoiceCallResponse,
    USSDMenuCreate, USSDMenuUpdate, USSDMenuResponse,
    USSDSessionCreate, USSDSessionUpdate, USSDSessionResponse
)
from ..models.notification import (
    NotificationType, NotificationChannel,
    NotificationStatus, NotificationPriority
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Notification endpoints
@router.post("", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new notification."""
    try:
        return await notification_service.create_notification(
            db,
            notification.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a notification by ID."""
    notification = await notification_service.get_notification(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("", response_model=List[NotificationResponse])
async def get_user_notifications(
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    status: Optional[NotificationStatus] = Query(None, description="Filter by status"),
    priority: Optional[NotificationPriority] = Query(None, description="Filter by priority"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user notifications with optional filters."""
    return await notification_service.get_user_notifications(
        db,
        current_user.id,
        notification_type=notification_type,
        channel=channel,
        status=status,
        priority=priority,
        start_date=start_date,
        end_date=end_date
    )

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a notification."""
    notification = await notification_service.get_notification(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    updated_notification = await notification_service.update_notification(
        db,
        notification_id,
        notification_update.dict(exclude_unset=True)
    )
    return updated_notification

# Template endpoints
@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new notification template."""
    try:
        return await notification_service.create_template(
            db,
            template.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a template by ID."""
    template = await notification_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_templates(
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification templates with optional filters."""
    return await notification_service.get_templates(
        db,
        notification_type=notification_type,
        channel=channel
    )

@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_template(
    template_id: int,
    template_update: NotificationTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a template."""
    template = await notification_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updated_template = await notification_service.update_template(
        db,
        template_id,
        template_update.dict(exclude_unset=True)
    )
    return updated_template

# Preference endpoints
@router.post("/preferences", response_model=NotificationPreferenceResponse)
async def create_preference(
    preference: NotificationPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new notification preference."""
    try:
        return await notification_service.create_preference(
            db,
            preference.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
async def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification preferences for the current user."""
    return await notification_service.get_user_preferences(db, current_user.id)

@router.put("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
async def update_preference(
    preference_id: int,
    preference_update: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a notification preference."""
    preference = await notification_service.update_preference(
        db,
        preference_id,
        preference_update.dict(exclude_unset=True)
    )
    if not preference or preference.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preference

# Log endpoints
@router.get("/{notification_id}/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get logs for a notification."""
    notification = await notification_service.get_notification(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return await notification_service.get_notification_logs(db, notification_id)

# Statistics endpoint
@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive notification statistics."""
    try:
        return await notification_service.get_notification_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WhatsApp Session endpoints
@router.post("/whatsapp/sessions", response_model=WhatsAppSessionResponse)
async def create_whatsapp_session(
    session: WhatsAppSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new WhatsApp session."""
    notification_service = NotificationService(db)
    return notification_service.create_whatsapp_session(session)

@router.put("/whatsapp/sessions/{session_id}", response_model=WhatsAppSessionResponse)
async def update_whatsapp_session(
    session_id: int,
    session_update: WhatsAppSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing WhatsApp session."""
    notification_service = NotificationService(db)
    updated_session = notification_service.update_whatsapp_session(
        session_id,
        session_update.dict(exclude_unset=True)
    )
    if not updated_session:
        raise HTTPException(status_code=404, detail="WhatsApp session not found")
    return updated_session

@router.get("/whatsapp/sessions", response_model=List[WhatsAppSessionResponse])
async def get_whatsapp_sessions(
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of WhatsApp sessions."""
    notification_service = NotificationService(db)
    return notification_service.get_whatsapp_sessions(patient_id, status, skip, limit)

# Voice Call endpoints
@router.post("/voice/calls", response_model=VoiceCallResponse)
async def create_voice_call(
    call: VoiceCallCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new voice call."""
    notification_service = NotificationService(db)
    return notification_service.create_voice_call(call)

@router.put("/voice/calls/{call_id}", response_model=VoiceCallResponse)
async def update_voice_call(
    call_id: int,
    call_update: VoiceCallUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing voice call."""
    notification_service = NotificationService(db)
    updated_call = notification_service.update_voice_call(
        call_id,
        call_update.dict(exclude_unset=True)
    )
    if not updated_call:
        raise HTTPException(status_code=404, detail="Voice call not found")
    return updated_call

@router.get("/voice/calls", response_model=List[VoiceCallResponse])
async def get_voice_calls(
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of voice calls."""
    notification_service = NotificationService(db)
    return notification_service.get_voice_calls(patient_id, status, skip, limit)

# USSD Menu endpoints
@router.post("/ussd/menus", response_model=USSDMenuResponse)
async def create_ussd_menu(
    menu: USSDMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new USSD menu."""
    notification_service = NotificationService(db)
    return notification_service.create_ussd_menu(menu, current_user.id)

@router.put("/ussd/menus/{menu_id}", response_model=USSDMenuResponse)
async def update_ussd_menu(
    menu_id: int,
    menu_update: USSDMenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing USSD menu."""
    notification_service = NotificationService(db)
    updated_menu = notification_service.update_ussd_menu(
        menu_id,
        menu_update.dict(exclude_unset=True)
    )
    if not updated_menu:
        raise HTTPException(status_code=404, detail="USSD menu not found")
    return updated_menu

@router.get("/ussd/menus", response_model=List[USSDMenuResponse])
async def get_ussd_menus(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of USSD menus."""
    notification_service = NotificationService(db)
    return notification_service.get_ussd_menus(is_active, skip, limit)

# USSD Session endpoints
@router.post("/ussd/sessions", response_model=USSDSessionResponse)
async def create_ussd_session(
    session: USSDSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new USSD session."""
    notification_service = NotificationService(db)
    return notification_service.create_ussd_session(session)

@router.put("/ussd/sessions/{session_id}", response_model=USSDSessionResponse)
async def update_ussd_session(
    session_id: int,
    session_update: USSDSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing USSD session."""
    notification_service = NotificationService(db)
    updated_session = notification_service.update_ussd_session(
        session_id,
        session_update.dict(exclude_unset=True)
    )
    if not updated_session:
        raise HTTPException(status_code=404, detail="USSD session not found")
    return updated_session

@router.get("/ussd/sessions", response_model=List[USSDSessionResponse])
async def get_ussd_sessions(
    patient_id: Optional[int] = None,
    menu_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of USSD sessions."""
    notification_service = NotificationService(db)
    return notification_service.get_ussd_sessions(patient_id, menu_id, skip, limit) 