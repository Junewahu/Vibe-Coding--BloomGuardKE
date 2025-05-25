from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class ReportType(str, enum.Enum):
    PATIENT_HEALTH = "patient_health"
    CHW_PERFORMANCE = "chw_performance"
    ADHERENCE = "adherence"
    RESOURCE_UTILIZATION = "resource_utilization"
    PROGRAM_EFFECTIVENESS = "program_effectiveness"
    CUSTOM = "custom"

class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MetricType(str, enum.Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    RATIO = "ratio"
    TREND = "trend"
    DISTRIBUTION = "distribution"

class DashboardType(str, enum.Enum):
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER = "user"
    CUSTOM = "custom"

class Report(Base):
    """Model for storing generated reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    parameters = Column(JSON)  # Report generation parameters
    data = Column(JSON)  # Report data
    format = Column(String, default="json")  # json, csv, pdf
    status = Column(String, default="completed")  # pending, processing, completed, failed
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    generator = relationship("User", back_populates="generated_reports")

class Metric(Base):
    """Model for tracking various metrics"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(Enum(MetricType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    value = Column(Float)
    unit = Column(String)
    context = Column(JSON)  # Additional context for the metric
    time_period = Column(String)  # daily, weekly, monthly, quarterly, yearly
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Dashboard(Base):
    """Model for storing dashboard configurations"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    layout = Column(JSON)  # Dashboard layout configuration
    widgets = Column(JSON)  # List of widget configurations
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboards")

class Widget(Base):
    """Model for storing widget configurations"""
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    widget_type = Column(String, nullable=False)  # chart, table, metric, etc.
    title = Column(String, nullable=False)
    description = Column(String)
    configuration = Column(JSON)  # Widget-specific configuration
    data_source = Column(JSON)  # Data source configuration
    refresh_interval = Column(Integer)  # Refresh interval in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

class Alert(Base):
    """Model for storing analytics alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    condition = Column(JSON)  # Alert condition configuration
    threshold = Column(Float)
    severity = Column(String)  # low, medium, high, critical
    message = Column(String)
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    metric = relationship("Metric", back_populates="alerts")

# Add relationships to User model
from .user import User
User.generated_reports = relationship("Report", back_populates="generator")
User.dashboards = relationship("Dashboard", back_populates="user") 