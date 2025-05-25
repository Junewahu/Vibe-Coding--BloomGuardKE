from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.follow_up import FollowUp
from ..models.notification import Notification
from ..models.response import Response
from ..services.risk_scoring import calculate_risk_score
from ..services.dashboard import dashboard_service
from ..schemas.dashboard import (
    DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    StaffAvailabilityCreate, StaffAvailabilityUpdate, StaffAvailabilityResponse,
    StaffLeaveCreate, StaffLeaveUpdate, StaffLeaveResponse,
    PerformanceMetricCreate, PerformanceMetricUpdate, PerformanceMetricResponse,
    DashboardNotificationCreate, DashboardNotificationUpdate, DashboardNotificationResponse,
    DashboardStats
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get overview statistics for the dashboard."""
    try:
        # Get date ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Calculate statistics
        total_patients = db.query(func.count(Patient.id)).scalar()
        new_patients_week = db.query(func.count(Patient.id)).filter(
            Patient.created_at >= week_ago
        ).scalar()
        
        total_appointments = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == current_user.id
        ).scalar()
        upcoming_appointments = db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.scheduled_date >= today
            )
        ).scalar()
        
        total_follow_ups = db.query(func.count(FollowUp.id)).filter(
            FollowUp.doctor_id == current_user.id
        ).scalar()
        pending_follow_ups = db.query(func.count(FollowUp.id)).filter(
            and_(
                FollowUp.doctor_id == current_user.id,
                FollowUp.status == "pending"
            )
        ).scalar()
        
        # Notification statistics
        notifications_sent = db.query(func.count(Notification.id)).filter(
            Notification.created_at >= month_ago
        ).scalar()
        notifications_delivered = db.query(func.count(Notification.id)).filter(
            and_(
                Notification.created_at >= month_ago,
                Notification.status == "delivered"
            )
        ).scalar()
        
        # Response statistics
        total_responses = db.query(func.count(Response.id)).filter(
            Response.created_at >= month_ago
        ).scalar()
        escalated_responses = db.query(func.count(Response.id)).filter(
            and_(
                Response.created_at >= month_ago,
                Response.status == "escalated"
            )
        ).scalar()
        
        return {
            "patients": {
                "total": total_patients,
                "new_this_week": new_patients_week
            },
            "appointments": {
                "total": total_appointments,
                "upcoming": upcoming_appointments
            },
            "follow_ups": {
                "total": total_follow_ups,
                "pending": pending_follow_ups
            },
            "notifications": {
                "sent": notifications_sent,
                "delivered": notifications_delivered,
                "delivery_rate": (notifications_delivered / notifications_sent * 100) if notifications_sent > 0 else 0
            },
            "responses": {
                "total": total_responses,
                "escalated": escalated_responses,
                "escalation_rate": (escalated_responses / total_responses * 100) if total_responses > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/appointments/timeline")
async def get_appointments_timeline(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get appointments timeline for the specified date range."""
    try:
        appointments = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.scheduled_date >= start_date,
                Appointment.scheduled_date <= end_date
            )
        ).all()
        
        return [{
            "id": apt.id,
            "patient_name": apt.patient.full_name,
            "scheduled_date": apt.scheduled_date,
            "duration": apt.duration,
            "status": apt.status,
            "type": apt.type
        } for apt in appointments]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/patients/risk-scores")
async def get_patients_risk_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk scores for all patients."""
    try:
        patients = db.query(Patient).all()
        risk_scores = []
        
        for patient in patients:
            score = calculate_risk_score(patient)
            risk_scores.append({
                "patient_id": patient.id,
                "patient_name": patient.full_name,
                "risk_score": score,
                "risk_level": "high" if score >= 7 else "medium" if score >= 4 else "low"
            })
        
        return sorted(risk_scores, key=lambda x: x["risk_score"], reverse=True)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/notifications/analytics")
async def get_notification_analytics(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification analytics for the specified date range."""
    try:
        notifications = db.query(Notification).filter(
            and_(
                Notification.created_at >= start_date,
                Notification.created_at <= end_date
            )
        ).all()
        
        # Calculate channel-wise statistics
        channel_stats = {}
        for notification in notifications:
            channel = notification.channel
            if channel not in channel_stats:
                channel_stats[channel] = {
                    "total": 0,
                    "delivered": 0,
                    "failed": 0
                }
            
            channel_stats[channel]["total"] += 1
            if notification.status == "delivered":
                channel_stats[channel]["delivered"] += 1
            elif notification.status == "failed":
                channel_stats[channel]["failed"] += 1
        
        # Calculate response rates
        response_rates = {}
        for channel, stats in channel_stats.items():
            responses = db.query(func.count(Response.id)).filter(
                and_(
                    Response.created_at >= start_date,
                    Response.created_at <= end_date,
                    Response.notification.has(channel=channel)
                )
            ).scalar()
            
            response_rates[channel] = (responses / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "channel_statistics": channel_stats,
            "response_rates": response_rates
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/follow-ups/analytics")
async def get_follow_up_analytics(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get follow-up analytics for the specified date range."""
    try:
        follow_ups = db.query(FollowUp).filter(
            and_(
                FollowUp.doctor_id == current_user.id,
                FollowUp.created_at >= start_date,
                FollowUp.created_at <= end_date
            )
        ).all()
        
        # Calculate type-wise statistics
        type_stats = {}
        for follow_up in follow_ups:
            follow_up_type = follow_up.type
            if follow_up_type not in type_stats:
                type_stats[follow_up_type] = {
                    "total": 0,
                    "completed": 0,
                    "cancelled": 0,
                    "no_show": 0
                }
            
            type_stats[follow_up_type]["total"] += 1
            if follow_up.status == "completed":
                type_stats[follow_up_type]["completed"] += 1
            elif follow_up.status == "cancelled":
                type_stats[follow_up_type]["cancelled"] += 1
            elif follow_up.status == "no_show":
                type_stats[follow_up_type]["no_show"] += 1
        
        # Calculate completion rates
        completion_rates = {}
        for follow_up_type, stats in type_stats.items():
            completion_rates[follow_up_type] = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "type_statistics": type_stats,
            "completion_rates": completion_rates
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/initialize", response_model=List[DashboardWidgetResponse])
async def initialize_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Initialize dashboard with default widgets."""
    try:
        return await dashboard_service.initialize_user_dashboard(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widgets", response_model=List[DashboardWidgetResponse])
async def get_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all widgets for the current user."""
    return await dashboard_service.get_user_widgets(db, current_user.id)

@router.post("/widgets", response_model=DashboardWidgetResponse)
async def create_widget(
    widget: DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dashboard widget."""
    try:
        return await dashboard_service.create_widget(
            db,
            current_user.id,
            widget.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_widget(
    widget_id: int,
    widget_update: DashboardWidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a dashboard widget."""
    widget = await dashboard_service.update_widget(
        db,
        widget_id,
        widget_update.dict(exclude_unset=True)
    )
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

@router.delete("/widgets/{widget_id}")
async def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a dashboard widget."""
    success = await dashboard_service.delete_widget(db, widget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"status": "success"}

@router.get("/availability", response_model=List[StaffAvailabilityResponse])
async def get_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get staff availability schedule."""
    return await dashboard_service.get_staff_availability(db, current_user.id)

@router.put("/availability", response_model=List[StaffAvailabilityResponse])
async def update_availability(
    availability: List[StaffAvailabilityCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update staff availability schedule."""
    try:
        return await dashboard_service.update_availability(
            db,
            current_user.id,
            [a.dict() for a in availability]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/leave", response_model=StaffLeaveResponse)
async def create_leave_request(
    leave: StaffLeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new leave request."""
    try:
        return await dashboard_service.create_leave_request(
            db,
            current_user.id,
            leave.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/leave/{leave_id}", response_model=StaffLeaveResponse)
async def update_leave_request(
    leave_id: int,
    leave_update: StaffLeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a leave request."""
    leave = await dashboard_service.update_leave_request(
        db,
        leave_id,
        leave_update.dict(exclude_unset=True)
    )
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave

@router.get("/leave", response_model=List[StaffLeaveResponse])
async def get_leave_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get leave requests with optional status filter."""
    return await dashboard_service.get_leave_requests(
        db,
        user_id=current_user.id,
        status=status
    )

@router.post("/metrics", response_model=PerformanceMetricResponse)
async def create_performance_metric(
    metric: PerformanceMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new performance metric."""
    try:
        return await dashboard_service.update_performance_metric(
            db,
            current_user.id,
            metric.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics", response_model=List[PerformanceMetricResponse])
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get performance metrics with date range."""
    return await dashboard_service.get_performance_metrics(
        db,
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.post("/notifications", response_model=DashboardNotificationResponse)
async def create_notification(
    notification: DashboardNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dashboard notification."""
    try:
        return await dashboard_service.create_notification(
            db,
            current_user.id,
            notification.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/notifications", response_model=List[DashboardNotificationResponse])
async def get_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user notifications with optional read status filter."""
    return await dashboard_service.get_notifications(
        db,
        current_user.id,
        is_read=is_read,
        limit=limit
    )

@router.put("/notifications/{notification_id}", response_model=DashboardNotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    notification = await dashboard_service.mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard statistics."""
    try:
        return await dashboard_service.get_dashboard_stats(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 