from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.calendar import EventType
from ..services.calendar import calendar_service
from ..schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
from .. import auth

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.post("/events", response_model=CalendarEventResponse)
async def create_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a new calendar event."""
    try:
        return await calendar_service.create_event(db, event.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get a calendar event by ID."""
    event = await calendar_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Update a calendar event."""
    event = await calendar_service.update_event(
        db,
        event_id,
        event_update.dict(exclude_unset=True)
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Delete a calendar event."""
    success = await calendar_service.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

@router.get("/events", response_model=List[CalendarEventResponse])
async def get_events(
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get calendar events with filters."""
    events = await calendar_service.get_events(
        db,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date
    )
    return events 