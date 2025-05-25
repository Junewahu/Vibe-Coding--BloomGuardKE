from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..database import get_db
from ..models.scheduling import ScheduleType, ScheduleStatus
from ..services.scheduling import scheduling_service, SchedulingService
from ..schemas.scheduling import (
    ScheduleRuleCreate,
    ScheduleRuleUpdate,
    ScheduleRuleResponse,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleReminderCreate,
    ScheduleReminderUpdate,
    ScheduleReminderResponse,
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate,
    ScheduleTemplateResponse,
    ScheduleOverrideCreate,
    ScheduleOverrideResponse,
    ScheduleStats,
    CustomProtocolCreate,
    CustomProtocolUpdate,
    CustomProtocolResponse,
    FollowUpScheduleCreate,
    FollowUpScheduleUpdate,
    FollowUpScheduleResponse,
    ScheduleAdjustmentCreate,
    ScheduleAdjustmentUpdate,
    ScheduleAdjustmentResponse
)
from .. import auth

router = APIRouter(prefix="/scheduling", tags=["scheduling"])

@router.post("/rules", response_model=ScheduleRuleResponse)
async def create_rule(
    rule: ScheduleRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Create a new scheduling rule."""
    try:
        service = SchedulingService(db)
        return service.create_schedule_rule(rule, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rules/{rule_id}", response_model=ScheduleRuleResponse)
async def get_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get a scheduling rule by ID."""
    rule = await scheduling_service.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=ScheduleRuleResponse)
async def update_rule(
    rule_id: int,
    rule_update: ScheduleRuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Update a scheduling rule."""
    try:
        service = SchedulingService(db)
        updated_rule = service.update_schedule_rule(rule_id, rule_update)
        if not updated_rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return updated_rule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule."""
    try:
        return await scheduling_service.create_schedule(db, schedule.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update a schedule."""
    schedule = await scheduling_service.update_schedule(
        db,
        schedule_id,
        schedule_update.dict(exclude_unset=True)
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    status: Optional[ScheduleStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get schedules with filters."""
    schedules = await scheduling_service.get_schedules(
        db,
        patient_id=patient_id,
        rule_id=rule_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return schedules

@router.post("/reminders", response_model=ScheduleReminderResponse)
async def create_reminder(
    reminder: ScheduleReminderCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule reminder."""
    try:
        return await scheduling_service.create_reminder(db, reminder.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/reminders/{reminder_id}", response_model=ScheduleReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_update: ScheduleReminderUpdate,
    db: Session = Depends(get_db)
):
    """Update a schedule reminder."""
    reminder = await scheduling_service.update_reminder(
        db,
        reminder_id,
        reminder_update.dict(exclude_unset=True)
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.get("/reminders", response_model=List[ScheduleReminderResponse])
async def get_reminders(
    schedule_id: Optional[int] = Query(None, description="Filter by schedule ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get reminders with filters."""
    reminders = await scheduling_service.get_reminders(
        db,
        schedule_id=schedule_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return reminders

@router.post("/templates", response_model=ScheduleTemplateResponse)
async def create_template(
    template: ScheduleTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule template."""
    try:
        return await scheduling_service.create_template(db, template.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/templates/{template_id}", response_model=ScheduleTemplateResponse)
async def update_template(
    template_id: int,
    template_update: ScheduleTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update a schedule template."""
    template = await scheduling_service.update_template(
        db,
        template_id,
        template_update.dict(exclude_unset=True)
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/overrides", response_model=ScheduleOverrideResponse)
async def create_override(
    override: ScheduleOverrideCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule override."""
    try:
        return await scheduling_service.create_override(db, override.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats", response_model=ScheduleStats)
async def get_schedule_stats(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Get comprehensive schedule statistics."""
    try:
        service = SchedulingService(db)
        return service.get_schedule_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedules/{schedule_id}/reschedule", response_model=ScheduleResponse)
async def reschedule_appointment(
    schedule_id: int,
    new_date: datetime,
    reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Reschedule an appointment."""
    schedule = await scheduling_service.reschedule_appointment(
        db,
        schedule_id,
        new_date,
        reason,
        current_user["id"]
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/schedules/handle-missed", response_model=List[ScheduleResponse])
async def handle_missed_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Handle missed appointments by marking them and creating reschedule events."""
    return await scheduling_service.handle_missed_appointments(db)

@router.post("/rules/moh/import", response_model=List[ScheduleRuleResponse])
async def import_moh_rules(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Import Ministry of Health immunization rules from a JSON file."""
    try:
        content = await file.read()
        rules_data = json.loads(content)
        
        # Validate rules data structure
        for rule in rules_data:
            if not all(key in rule for key in ["name", "protocol"]):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid rule format. Each rule must have 'name' and 'protocol' fields."
                )
        
        rules = await scheduling_service.import_moh_rules(db, rules_data)
        return rules
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/custom", response_model=ScheduleRuleResponse)
async def create_custom_rule(
    name: str,
    schedule_type: ScheduleType,
    protocol: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Create a custom scheduling rule."""
    try:
        rule = await scheduling_service.create_custom_rule(
            db,
            name,
            schedule_type,
            protocol
        )
        return rule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schedules/missed", response_model=List[ScheduleResponse])
async def get_missed_schedules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get all missed schedules."""
    schedules = await scheduling_service.get_schedules(
        db,
        status=ScheduleStatus.MISSED
    )
    return schedules

@router.get("/schedules/rescheduled", response_model=List[ScheduleResponse])
async def get_rescheduled_schedules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_active_user)
):
    """Get all rescheduled schedules."""
    schedules = await scheduling_service.get_schedules(
        db,
        status=ScheduleStatus.RESCHEDULED
    )
    return schedules

@router.get("/rules", response_model=List[ScheduleRuleResponse])
async def get_schedule_rules(
    rule_type: Optional[ScheduleType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Get schedule rules with optional filters"""
    try:
        service = SchedulingService(db)
        return service.get_schedule_rules(rule_type, is_active)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/protocols", response_model=CustomProtocolResponse)
async def create_custom_protocol(
    protocol: CustomProtocolCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Create a new custom protocol"""
    try:
        service = SchedulingService(db)
        return service.create_custom_protocol(protocol, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/protocols/{protocol_id}", response_model=CustomProtocolResponse)
async def update_custom_protocol(
    protocol_id: int,
    protocol: CustomProtocolUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Update an existing custom protocol"""
    try:
        service = SchedulingService(db)
        updated_protocol = service.update_custom_protocol(protocol_id, protocol)
        if not updated_protocol:
            raise HTTPException(status_code=404, detail="Custom protocol not found")
        return updated_protocol
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/protocols", response_model=List[CustomProtocolResponse])
async def get_custom_protocols(
    protocol_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Get custom protocols with optional filters"""
    try:
        service = SchedulingService(db)
        return service.get_custom_protocols(protocol_type, is_active)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/follow-ups", response_model=FollowUpScheduleResponse)
async def create_follow_up_schedule(
    schedule: FollowUpScheduleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Create a new follow-up schedule"""
    try:
        service = SchedulingService(db)
        return service.create_follow_up_schedule(schedule, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/follow-ups/{schedule_id}", response_model=FollowUpScheduleResponse)
async def update_follow_up_schedule(
    schedule_id: int,
    schedule: FollowUpScheduleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Update an existing follow-up schedule"""
    try:
        service = SchedulingService(db)
        updated_schedule = service.update_follow_up_schedule(schedule_id, schedule)
        if not updated_schedule:
            raise HTTPException(status_code=404, detail="Follow-up schedule not found")
        return updated_schedule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/follow-ups", response_model=List[FollowUpScheduleResponse])
async def get_follow_up_schedules(
    patient_id: Optional[int] = None,
    schedule_type: Optional[ScheduleType] = None,
    status: Optional[ScheduleStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Get follow-up schedules with optional filters"""
    try:
        service = SchedulingService(db)
        return service.get_follow_up_schedules(patient_id, schedule_type, status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/adjustments", response_model=ScheduleAdjustmentResponse)
async def create_schedule_adjustment(
    adjustment: ScheduleAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Create a new schedule adjustment"""
    try:
        service = SchedulingService(db)
        return service.create_schedule_adjustment(adjustment, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/adjustments/{adjustment_id}", response_model=ScheduleAdjustmentResponse)
async def update_schedule_adjustment(
    adjustment_id: int,
    adjustment: ScheduleAdjustmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Update an existing schedule adjustment"""
    try:
        service = SchedulingService(db)
        updated_adjustment = service.update_schedule_adjustment(adjustment_id, adjustment)
        if not updated_adjustment:
            raise HTTPException(status_code=404, detail="Schedule adjustment not found")
        return updated_adjustment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/adjustments", response_model=List[ScheduleAdjustmentResponse])
async def get_schedule_adjustments(
    schedule_id: Optional[int] = None,
    adjustment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Get schedule adjustments with optional filters"""
    try:
        service = SchedulingService(db)
        return service.get_schedule_adjustments(schedule_id, adjustment_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 