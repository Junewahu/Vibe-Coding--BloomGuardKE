from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.analytics import (
    MessageDeliveryMetrics,
    NHIFClaimMetrics,
    PatientEngagementMetrics,
    FacilityPerformanceMetrics
)
from ..schemas.analytics import (
    MessageDeliveryMetricsCreate,
    NHIFClaimMetricsCreate,
    PatientEngagementMetricsCreate,
    FacilityPerformanceMetricsCreate
)

# Message Delivery Metrics
def create_message_metrics(
    db: Session,
    metrics: MessageDeliveryMetricsCreate
) -> MessageDeliveryMetrics:
    db_metrics = MessageDeliveryMetrics(**metrics.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_message_metrics(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[MessageDeliveryMetrics]:
    return db.query(MessageDeliveryMetrics).filter(
        MessageDeliveryMetrics.facility_id == facility_id,
        MessageDeliveryMetrics.date >= start_date,
        MessageDeliveryMetrics.date <= end_date
    ).all()

def get_message_metrics_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    metrics = get_message_metrics(db, facility_id, start_date, end_date)
    if not metrics:
        return {
            "total_sent": 0,
            "delivery_rate": 0.0,
            "average_delivery_time": 0.0
        }
    
    total_sent = sum(m.total_sent for m in metrics)
    total_delivered = sum(m.delivered for m in metrics)
    total_delivery_time = sum(m.average_delivery_time * m.delivered for m in metrics)
    
    return {
        "total_sent": total_sent,
        "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0.0,
        "average_delivery_time": total_delivery_time / total_delivered if total_delivered > 0 else 0.0
    }

# NHIF Claim Metrics
def create_claim_metrics(
    db: Session,
    metrics: NHIFClaimMetricsCreate
) -> NHIFClaimMetrics:
    db_metrics = NHIFClaimMetrics(**metrics.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_claim_metrics(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[NHIFClaimMetrics]:
    return db.query(NHIFClaimMetrics).filter(
        NHIFClaimMetrics.facility_id == facility_id,
        NHIFClaimMetrics.date >= start_date,
        NHIFClaimMetrics.date <= end_date
    ).all()

def get_claim_metrics_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    metrics = get_claim_metrics(db, facility_id, start_date, end_date)
    if not metrics:
        return {
            "total_claims": 0,
            "approval_rate": 0.0,
            "total_amount_approved": 0.0
        }
    
    total_claims = sum(m.total_claims for m in metrics)
    total_approved = sum(m.approved_claims for m in metrics)
    total_amount = sum(m.total_amount_approved for m in metrics)
    
    return {
        "total_claims": total_claims,
        "approval_rate": (total_approved / total_claims * 100) if total_claims > 0 else 0.0,
        "total_amount_approved": total_amount
    }

# Patient Engagement Metrics
def create_engagement_metrics(
    db: Session,
    metrics: PatientEngagementMetricsCreate
) -> PatientEngagementMetrics:
    db_metrics = PatientEngagementMetrics(**metrics.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_engagement_metrics(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[PatientEngagementMetrics]:
    return db.query(PatientEngagementMetrics).filter(
        PatientEngagementMetrics.facility_id == facility_id,
        PatientEngagementMetrics.date >= start_date,
        PatientEngagementMetrics.date <= end_date
    ).all()

def get_engagement_metrics_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    metrics = get_engagement_metrics(db, facility_id, start_date, end_date)
    if not metrics:
        return {
            "total_patients": 0,
            "active_patients": 0,
            "satisfaction_score": 0.0
        }
    
    latest_metrics = metrics[-1]
    return {
        "total_patients": latest_metrics.total_patients,
        "active_patients": latest_metrics.active_patients,
        "satisfaction_score": latest_metrics.patient_satisfaction_score
    }

# Facility Performance Metrics
def create_performance_metrics(
    db: Session,
    metrics: FacilityPerformanceMetricsCreate
) -> FacilityPerformanceMetrics:
    db_metrics = FacilityPerformanceMetrics(**metrics.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_performance_metrics(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[FacilityPerformanceMetrics]:
    return db.query(FacilityPerformanceMetrics).filter(
        FacilityPerformanceMetrics.facility_id == facility_id,
        FacilityPerformanceMetrics.date >= start_date,
        FacilityPerformanceMetrics.date <= end_date
    ).all()

def get_performance_metrics_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    metrics = get_performance_metrics(db, facility_id, start_date, end_date)
    if not metrics:
        return {
            "total_revenue": 0.0,
            "average_wait_time": 0.0,
            "appointment_completion_rate": 0.0
        }
    
    total_revenue = sum(m.revenue for m in metrics)
    total_wait_time = sum(m.average_wait_time * m.completed_appointments for m in metrics)
    total_completed = sum(m.completed_appointments for m in metrics)
    total_appointments = sum(m.total_appointments for m in metrics)
    
    return {
        "total_revenue": total_revenue,
        "average_wait_time": total_wait_time / total_completed if total_completed > 0 else 0.0,
        "appointment_completion_rate": (total_completed / total_appointments * 100) if total_appointments > 0 else 0.0
    }

# Overall Analytics Summary
def get_analytics_summary(
    db: Session,
    facility_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    message_summary = get_message_metrics_summary(db, facility_id, start_date, end_date)
    claim_summary = get_claim_metrics_summary(db, facility_id, start_date, end_date)
    engagement_summary = get_engagement_metrics_summary(db, facility_id, start_date, end_date)
    performance_summary = get_performance_metrics_summary(db, facility_id, start_date, end_date)
    
    return {
        "message_delivery": message_summary,
        "nhif_claims": claim_summary,
        "patient_engagement": engagement_summary,
        "facility_performance": performance_summary
    } 