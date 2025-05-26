from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..services.incentive_service import IncentiveService
from ..schemas.incentives import (
    Incentive,
    IncentiveCreate,
    IncentiveUpdate,
    IncentiveRule,
    IncentiveRuleCreate,
    IncentiveRuleUpdate,
    IncentivePayment,
    IncentivePaymentCreate,
    IncentivePaymentUpdate,
    IncentiveResponse,
    IncentiveSummary
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/incentives",
    tags=["incentives"]
)

# Incentive Rule Endpoints
@router.post("/rules", response_model=IncentiveRule)
def create_incentive_rule(
    rule: IncentiveRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new incentive rule."""
    service = IncentiveService(db)
    return service.create_incentive_rule(rule)

@router.get("/rules", response_model=List[IncentiveRule])
def get_incentive_rules(
    facility_id: int,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all incentive rules for a facility."""
    service = IncentiveService(db)
    return service.get_incentive_rules(facility_id, skip, limit, is_active)

@router.get("/rules/{rule_id}", response_model=IncentiveRule)
def get_incentive_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific incentive rule."""
    service = IncentiveService(db)
    rule = service.get_incentive_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Incentive rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=IncentiveRule)
def update_incentive_rule(
    rule_id: int,
    rule: IncentiveRuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an incentive rule."""
    service = IncentiveService(db)
    updated_rule = service.update_incentive_rule(rule_id, rule)
    if not updated_rule:
        raise HTTPException(status_code=404, detail="Incentive rule not found")
    return updated_rule

# Incentive Endpoints
@router.post("/calculate", response_model=Incentive)
def calculate_incentive(
    facility_id: int,
    user_id: int,
    incentive_type: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate an incentive for a user."""
    service = IncentiveService(db)
    
    if incentive_type == "performance":
        incentive = service.calculate_performance_incentive(facility_id, user_id, start_date, end_date)
    elif incentive_type == "attendance":
        incentive = service.calculate_attendance_incentive(facility_id, user_id, start_date, end_date)
    elif incentive_type == "patient_satisfaction":
        incentive = service.calculate_patient_satisfaction_incentive(facility_id, user_id, start_date, end_date)
    elif incentive_type == "quality_care":
        incentive = service.calculate_quality_care_incentive(facility_id, user_id, start_date, end_date)
    else:
        raise HTTPException(status_code=400, detail="Invalid incentive type")
    
    if not incentive:
        raise HTTPException(status_code=404, detail="No applicable incentive rule found")
    return incentive

@router.get("/", response_model=List[Incentive])
def get_incentives(
    facility_id: int,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all incentives for a facility."""
    service = IncentiveService(db)
    return service.get_incentives(facility_id, user_id, status, skip, limit)

@router.get("/{incentive_id}", response_model=Incentive)
def get_incentive(
    incentive_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific incentive."""
    service = IncentiveService(db)
    incentive = service.get_incentive(incentive_id)
    if not incentive:
        raise HTTPException(status_code=404, detail="Incentive not found")
    return incentive

@router.put("/{incentive_id}", response_model=Incentive)
def update_incentive(
    incentive_id: int,
    incentive: IncentiveUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an incentive."""
    service = IncentiveService(db)
    updated_incentive = service.update_incentive(incentive_id, incentive)
    if not updated_incentive:
        raise HTTPException(status_code=404, detail="Incentive not found")
    return updated_incentive

@router.post("/{incentive_id}/approve", response_model=Incentive)
def approve_incentive(
    incentive_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve an incentive."""
    service = IncentiveService(db)
    incentive = service.approve_incentive(incentive_id, current_user.id)
    if not incentive:
        raise HTTPException(status_code=404, detail="Incentive not found")
    return incentive

@router.post("/{incentive_id}/reject", response_model=Incentive)
def reject_incentive(
    incentive_id: int,
    notes: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reject an incentive."""
    service = IncentiveService(db)
    incentive = service.reject_incentive(incentive_id, current_user.id, notes)
    if not incentive:
        raise HTTPException(status_code=404, detail="Incentive not found")
    return incentive

# Incentive Payment Endpoints
@router.post("/{incentive_id}/payments", response_model=IncentivePayment)
def create_incentive_payment(
    incentive_id: int,
    payment: IncentivePaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a payment for an incentive."""
    service = IncentiveService(db)
    payment_record = service.process_incentive_payment(
        incentive_id,
        payment.payment_date,
        payment.payment_method,
        payment.payment_reference,
        payment.notes
    )
    if not payment_record:
        raise HTTPException(status_code=404, detail="Incentive not found or not approved")
    return payment_record

@router.get("/{incentive_id}/payments", response_model=List[IncentivePayment])
def get_incentive_payments(
    incentive_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all payments for an incentive."""
    service = IncentiveService(db)
    return service.get_incentive_payments(incentive_id)

# Analytics Endpoints
@router.get("/summary/facility/{facility_id}", response_model=IncentiveSummary)
def get_facility_incentive_summary(
    facility_id: int,
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get incentive summary for a facility."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    service = IncentiveService(db)
    return service.get_incentive_summary(facility_id, start_date, end_date)

@router.get("/summary/user/{user_id}", response_model=IncentiveSummary)
def get_user_incentive_summary(
    user_id: int,
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get incentive summary for a user."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    service = IncentiveService(db)
    return service.get_user_incentive_summary(user_id, start_date, end_date) 