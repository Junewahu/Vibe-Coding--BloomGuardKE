from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.incentives import Incentive, IncentiveRule, IncentivePayment
from ..schemas.incentives import (
    IncentiveCreate,
    IncentiveUpdate,
    IncentiveRuleCreate,
    IncentiveRuleUpdate,
    IncentivePaymentCreate,
    IncentivePaymentUpdate
)

# Incentive Rule CRUD
def create_incentive_rule(
    db: Session,
    rule: IncentiveRuleCreate
) -> IncentiveRule:
    db_rule = IncentiveRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_incentive_rule(
    db: Session,
    rule_id: int
) -> Optional[IncentiveRule]:
    return db.query(IncentiveRule).filter(IncentiveRule.id == rule_id).first()

def get_incentive_rules(
    db: Session,
    facility_id: int,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[IncentiveRule]:
    query = db.query(IncentiveRule).filter(IncentiveRule.facility_id == facility_id)
    if is_active is not None:
        query = query.filter(IncentiveRule.is_active == is_active)
    return query.offset(skip).limit(limit).all()

def update_incentive_rule(
    db: Session,
    rule_id: int,
    rule: IncentiveRuleUpdate
) -> Optional[IncentiveRule]:
    db_rule = get_incentive_rule(db, rule_id)
    if db_rule:
        update_data = rule.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        db.commit()
        db.refresh(db_rule)
    return db_rule

# Incentive CRUD
def create_incentive(
    db: Session,
    incentive: IncentiveCreate
) -> Incentive:
    db_incentive = Incentive(**incentive.dict())
    db.add(db_incentive)
    db.commit()
    db.refresh(db_incentive)
    return db_incentive

def get_incentive(
    db: Session,
    incentive_id: int
) -> Optional[Incentive]:
    return db.query(Incentive).filter(Incentive.id == incentive_id).first()

def get_incentives(
    db: Session,
    facility_id: int,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Incentive]:
    query = db.query(Incentive).filter(Incentive.facility_id == facility_id)
    if user_id:
        query = query.filter(Incentive.user_id == user_id)
    if status:
        query = query.filter(Incentive.status == status)
    return query.offset(skip).limit(limit).all()

def update_incentive(
    db: Session,
    incentive_id: int,
    incentive: IncentiveUpdate
) -> Optional[Incentive]:
    db_incentive = get_incentive(db, incentive_id)
    if db_incentive:
        update_data = incentive.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_incentive, field, value)
        db.commit()
        db.refresh(db_incentive)
    return db_incentive

def approve_incentive(
    db: Session,
    incentive_id: int,
    approver_id: int
) -> Optional[Incentive]:
    db_incentive = get_incentive(db, incentive_id)
    if db_incentive:
        db_incentive.status = "approved"
        db_incentive.approved_by = approver_id
        db_incentive.approved_at = datetime.utcnow()
        db.commit()
        db.refresh(db_incentive)
    return db_incentive

def reject_incentive(
    db: Session,
    incentive_id: int,
    approver_id: int,
    notes: str
) -> Optional[Incentive]:
    db_incentive = get_incentive(db, incentive_id)
    if db_incentive:
        db_incentive.status = "rejected"
        db_incentive.approved_by = approver_id
        db_incentive.approved_at = datetime.utcnow()
        db_incentive.notes = notes
        db.commit()
        db.refresh(db_incentive)
    return db_incentive

# Incentive Payment CRUD
def create_incentive_payment(
    db: Session,
    payment: IncentivePaymentCreate
) -> IncentivePayment:
    db_payment = IncentivePayment(**payment.dict())
    db.add(db_payment)
    
    # Update incentive status
    db_incentive = get_incentive(db, payment.incentive_id)
    if db_incentive:
        db_incentive.status = "paid"
        db_incentive.payment_date = payment.payment_date
        db_incentive.payment_reference = payment.payment_reference
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_incentive_payment(
    db: Session,
    payment_id: int
) -> Optional[IncentivePayment]:
    return db.query(IncentivePayment).filter(IncentivePayment.id == payment_id).first()

def get_incentive_payments(
    db: Session,
    incentive_id: int
) -> List[IncentivePayment]:
    return db.query(IncentivePayment).filter(
        IncentivePayment.incentive_id == incentive_id
    ).all()

def update_incentive_payment(
    db: Session,
    payment_id: int,
    payment: IncentivePaymentUpdate
) -> Optional[IncentivePayment]:
    db_payment = get_incentive_payment(db, payment_id)
    if db_payment:
        update_data = payment.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        db.commit()
        db.refresh(db_payment)
    return db_payment

# Analytics Functions
def get_incentive_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    incentives = db.query(Incentive).filter(
        Incentive.facility_id == facility_id,
        Incentive.created_at >= start_date,
        Incentive.created_at <= end_date
    ).all()
    
    summary = {
        "total_incentives": len(incentives),
        "total_amount": sum(i.total_amount for i in incentives),
        "pending_incentives": sum(1 for i in incentives if i.status == "pending"),
        "approved_incentives": sum(1 for i in incentives if i.status == "approved"),
        "paid_incentives": sum(1 for i in incentives if i.status == "paid"),
        "rejected_incentives": sum(1 for i in incentives if i.status == "rejected"),
        "by_type": {},
        "by_period": {},
        "recent_incentives": sorted(incentives, key=lambda x: x.created_at, reverse=True)[:5]
    }
    
    # Calculate counts by type and period
    for incentive in incentives:
        summary["by_type"][incentive.incentive_type] = summary["by_type"].get(incentive.incentive_type, 0) + 1
        summary["by_period"][incentive.period] = summary["by_period"].get(incentive.period, 0) + 1
    
    return summary

def get_user_incentive_summary(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    incentives = db.query(Incentive).filter(
        Incentive.user_id == user_id,
        Incentive.created_at >= start_date,
        Incentive.created_at <= end_date
    ).all()
    
    return {
        "total_incentives": len(incentives),
        "total_amount": sum(i.total_amount for i in incentives),
        "by_type": {i.incentive_type: sum(1 for inc in incentives if inc.incentive_type == i.incentive_type) for i in incentives},
        "by_period": {i.period: sum(1 for inc in incentives if inc.period == i.period) for i in incentives},
        "recent_incentives": sorted(incentives, key=lambda x: x.created_at, reverse=True)[:5]
    } 