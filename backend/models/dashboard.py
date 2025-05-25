from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class DashboardWidgetType(str, enum.Enum):
    APPOINTMENT_STATS = "appointment_stats"
    PATIENT_RESPONSES = "patient_responses"
    FOLLOW_UPS = "follow_ups"
    PERFORMANCE_METRICS = "performance_metrics"
    STAFF_SCHEDULE = "staff_schedule"
    CUSTOM = "custom"

class DashboardWidget(Base):
    """Model for dashboard widgets"""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    widget_type = Column(Enum(DashboardWidgetType), nullable=False)
    title = Column(String(100), nullable=False)
    position = Column(Integer, nullable=False)  # For ordering widgets
    size = Column(String(20), nullable=False)  # e.g., "small", "medium", "large"
    config = Column(JSON, nullable=True)  # Widget-specific configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")

class StaffAvailability(Base):
    """Model for staff availability"""
    __tablename__ = "staff_availability"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 for Monday-Sunday
    start_time = Column(String(5), nullable=False)  # Format: "HH:MM"
    end_time = Column(String(5), nullable=False)  # Format: "HH:MM"
    is_available = Column(Boolean, default=True)
    break_start = Column(String(5), nullable=True)  # Format: "HH:MM"
    break_end = Column(String(5), nullable=True)  # Format: "HH:MM"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="availability")

class StaffLeave(Base):
    """Model for staff leave records"""
    __tablename__ = "staff_leave"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    leave_type = Column(String(50), nullable=False)  # e.g., "annual", "sick", "emergency"
    status = Column(String(20), nullable=False)  # "pending", "approved", "rejected"
    reason = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="leave_records")
    approver = relationship("User", foreign_keys=[approved_by])

class PerformanceMetric(Base):
    """Model for staff performance metrics"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., "appointments", "responses", "follow_ups"
    value = Column(Float, nullable=False)
    target = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="performance_metrics")

class DashboardNotification(Base):
    """Model for dashboard notifications"""
    __tablename__ = "dashboard_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # e.g., "appointment", "response", "follow_up"
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboard_notifications") 