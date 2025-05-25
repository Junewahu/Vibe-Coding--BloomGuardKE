from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.calendar import CalendarEvent
from ..schemas.calendar import CalendarEventCreate, CalendarEventUpdate

class CalendarService:
    def __init__(self):
        pass

    async def create_event(self, db: Session, event_data: Dict[str, Any]) -> CalendarEvent:
        """Create a new calendar event."""
        event = CalendarEvent(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    async def get_event(self, db: Session, event_id: int) -> Optional[CalendarEvent]:
        """Get a calendar event by ID."""
        return db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    async def update_event(self, db: Session, event_id: int, event_data: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Update a calendar event."""
        event = await self.get_event(db, event_id)
        if not event:
            return None

        for key, value in event_data.items():
            setattr(event, key, value)

        db.commit()
        db.refresh(event)
        return event

    async def delete_event(self, db: Session, event_id: int) -> bool:
        """Delete a calendar event."""
        event = await self.get_event(db, event_id)
        if not event:
            return False

        db.delete(event)
        db.commit()
        return True

    async def get_events(
        self,
        db: Session,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Get calendar events with filters."""
        query = db.query(CalendarEvent)

        if event_type:
            query = query.filter(CalendarEvent.event_type == event_type)
        if start_date:
            query = query.filter(CalendarEvent.start_time >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.end_time <= end_date)

        return query.all()

# Create a singleton instance
calendar_service = CalendarService() 