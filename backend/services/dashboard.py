from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from ..models.dashboard import (
    DashboardWidget, StaffAvailability, StaffLeave,
    PerformanceMetric, DashboardNotification, DashboardWidgetType
)
from ..models.appointment import Appointment, AppointmentStatus
from ..models.response import PatientResponse, ResponseStatus
from ..models.follow_up import FollowUp, FollowUpStatus

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self):
        self.default_widgets = {
            DashboardWidgetType.APPOINTMENT_STATS: {
                "title": "Appointment Statistics",
                "size": "medium",
                "position": 0
            },
            DashboardWidgetType.PATIENT_RESPONSES: {
                "title": "Patient Responses",
                "size": "medium",
                "position": 1
            },
            DashboardWidgetType.FOLLOW_UPS: {
                "title": "Follow-ups",
                "size": "medium",
                "position": 2
            },
            DashboardWidgetType.PERFORMANCE_METRICS: {
                "title": "Performance Metrics",
                "size": "large",
                "position": 3
            },
            DashboardWidgetType.STAFF_SCHEDULE: {
                "title": "Staff Schedule",
                "size": "medium",
                "position": 4
            }
        }

    async def initialize_user_dashboard(
        self,
        db: Session,
        user_id: int
    ) -> List[DashboardWidget]:
        """Initialize dashboard with default widgets for a new user."""
        widgets = []
        for widget_type, config in self.default_widgets.items():
            widget = DashboardWidget(
                user_id=user_id,
                widget_type=widget_type,
                title=config["title"],
                position=config["position"],
                size=config["size"],
                is_active=True
            )
            db.add(widget)
            widgets.append(widget)
        
        db.commit()
        for widget in widgets:
            db.refresh(widget)
        return widgets

    async def get_user_widgets(
        self,
        db: Session,
        user_id: int
    ) -> List[DashboardWidget]:
        """Get all widgets for a user."""
        return db.query(DashboardWidget)\
            .filter(DashboardWidget.user_id == user_id)\
            .order_by(DashboardWidget.position)\
            .all()

    async def create_widget(
        self,
        db: Session,
        user_id: int,
        widget_data: Dict[str, Any]
    ) -> DashboardWidget:
        """Create a new dashboard widget."""
        widget = DashboardWidget(user_id=user_id, **widget_data)
        db.add(widget)
        db.commit()
        db.refresh(widget)
        return widget

    async def update_widget(
        self,
        db: Session,
        widget_id: int,
        widget_data: Dict[str, Any]
    ) -> Optional[DashboardWidget]:
        """Update a dashboard widget."""
        widget = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        if not widget:
            return None

        for key, value in widget_data.items():
            setattr(widget, key, value)

        db.commit()
        db.refresh(widget)
        return widget

    async def delete_widget(
        self,
        db: Session,
        widget_id: int
    ) -> bool:
        """Delete a dashboard widget."""
        widget = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        if not widget:
            return False

        db.delete(widget)
        db.commit()
        return True

    async def get_staff_availability(
        self,
        db: Session,
        user_id: int
    ) -> List[StaffAvailability]:
        """Get staff availability schedule."""
        return db.query(StaffAvailability)\
            .filter(StaffAvailability.user_id == user_id)\
            .order_by(StaffAvailability.day_of_week)\
            .all()

    async def update_availability(
        self,
        db: Session,
        user_id: int,
        availability_data: List[Dict[str, Any]]
    ) -> List[StaffAvailability]:
        """Update staff availability schedule."""
        # Delete existing availability
        db.query(StaffAvailability)\
            .filter(StaffAvailability.user_id == user_id)\
            .delete()

        # Create new availability records
        availability_records = []
        for data in availability_data:
            availability = StaffAvailability(user_id=user_id, **data)
            db.add(availability)
            availability_records.append(availability)

        db.commit()
        for record in availability_records:
            db.refresh(record)
        return availability_records

    async def create_leave_request(
        self,
        db: Session,
        user_id: int,
        leave_data: Dict[str, Any]
    ) -> StaffLeave:
        """Create a new leave request."""
        leave = StaffLeave(user_id=user_id, **leave_data)
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave

    async def update_leave_request(
        self,
        db: Session,
        leave_id: int,
        leave_data: Dict[str, Any]
    ) -> Optional[StaffLeave]:
        """Update a leave request."""
        leave = db.query(StaffLeave).filter(StaffLeave.id == leave_id).first()
        if not leave:
            return None

        for key, value in leave_data.items():
            setattr(leave, key, value)

        db.commit()
        db.refresh(leave)
        return leave

    async def get_leave_requests(
        self,
        db: Session,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[StaffLeave]:
        """Get leave requests with optional filters."""
        query = db.query(StaffLeave)
        if user_id:
            query = query.filter(StaffLeave.user_id == user_id)
        if status:
            query = query.filter(StaffLeave.status == status)
        return query.order_by(StaffLeave.start_date).all()

    async def update_performance_metric(
        self,
        db: Session,
        user_id: int,
        metric_data: Dict[str, Any]
    ) -> PerformanceMetric:
        """Update a performance metric."""
        metric = PerformanceMetric(user_id=user_id, **metric_data)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    async def get_performance_metrics(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PerformanceMetric]:
        """Get performance metrics with date range."""
        query = db.query(PerformanceMetric)\
            .filter(PerformanceMetric.user_id == user_id)
        
        if start_date:
            query = query.filter(PerformanceMetric.date >= start_date)
        if end_date:
            query = query.filter(PerformanceMetric.date <= end_date)
        
        return query.order_by(PerformanceMetric.date).all()

    async def create_notification(
        self,
        db: Session,
        user_id: int,
        notification_data: Dict[str, Any]
    ) -> DashboardNotification:
        """Create a new dashboard notification."""
        notification = DashboardNotification(user_id=user_id, **notification_data)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    async def get_notifications(
        self,
        db: Session,
        user_id: int,
        is_read: Optional[bool] = None,
        limit: int = 10
    ) -> List[DashboardNotification]:
        """Get user notifications with optional read status filter."""
        query = db.query(DashboardNotification)\
            .filter(DashboardNotification.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(DashboardNotification.is_read == is_read)
        
        return query.order_by(DashboardNotification.created_at.desc())\
            .limit(limit)\
            .all()

    async def mark_notification_read(
        self,
        db: Session,
        notification_id: int
    ) -> Optional[DashboardNotification]:
        """Mark a notification as read."""
        notification = db.query(DashboardNotification)\
            .filter(DashboardNotification.id == notification_id)\
            .first()
        
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        return notification

    async def get_dashboard_stats(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics."""
        # Get appointment statistics
        total_appointments = db.query(Appointment)\
            .filter(Appointment.doctor_id == user_id)\
            .count()
        
        upcoming_appointments = db.query(Appointment)\
            .filter(
                and_(
                    Appointment.doctor_id == user_id,
                    Appointment.status == AppointmentStatus.SCHEDULED,
                    Appointment.scheduled_time >= datetime.utcnow()
                )
            )\
            .count()

        # Get response statistics
        pending_responses = db.query(PatientResponse)\
            .filter(
                and_(
                    PatientResponse.status == ResponseStatus.RECEIVED,
                    PatientResponse.reminder.has(doctor_id=user_id)
                )
            )\
            .count()

        # Get follow-up statistics
        pending_follow_ups = db.query(FollowUp)\
            .filter(
                and_(
                    FollowUp.status == FollowUpStatus.PENDING,
                    FollowUp.assigned_to_id == user_id
                )
            )\
            .count()

        # Get performance metrics
        metrics = await self.get_performance_metrics(
            db,
            user_id,
            start_date=datetime.utcnow() - timedelta(days=30)
        )
        performance_metrics = {
            metric.metric_type: metric.value
            for metric in metrics
        }

        # Get recent notifications
        recent_notifications = await self.get_notifications(
            db,
            user_id,
            is_read=False,
            limit=5
        )

        # Get staff availability
        staff_availability = await self.get_staff_availability(db, user_id)

        # Get pending leave requests
        leave_requests = await self.get_leave_requests(
            db,
            user_id=user_id,
            status="pending"
        )

        return {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming_appointments,
            "pending_responses": pending_responses,
            "pending_follow_ups": pending_follow_ups,
            "performance_metrics": performance_metrics,
            "recent_notifications": recent_notifications,
            "staff_availability": staff_availability,
            "leave_requests": leave_requests
        }

# Create singleton instance
dashboard_service = DashboardService() 