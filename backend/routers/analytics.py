from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..services.analytics import analytics_service
from ..schemas.analytics import (
    ReportCreate, ReportUpdate, ReportResponse,
    AnalyticsMetricCreate, AnalyticsMetricUpdate, AnalyticsMetricResponse,
    AnalyticsDashboardCreate, AnalyticsDashboardUpdate, AnalyticsDashboardResponse,
    AnalyticsWidgetCreate, AnalyticsWidgetUpdate, AnalyticsWidgetResponse,
    AnalyticsExportCreate, AnalyticsExportUpdate, AnalyticsExportResponse,
    AnalyticsStats,
    MetricCreate,
    MetricUpdate,
    MetricResponse,
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    WidgetCreate,
    WidgetUpdate,
    WidgetResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    ReportStats,
    MetricStats,
    DashboardStats,
    AlertStats
)
from ..models.analytics import ReportType, ReportFormat, ReportStatus, AnalyticsMetricType, DashboardType, MetricType

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Reports Endpoints
@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new report."""
    try:
        return await analytics_service.create_report(
            db,
            current_user.id,
            report.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a report by ID."""
    report = await analytics_service.get_report(db, report_id)
    if not report or report.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/reports", response_model=List[ReportResponse])
async def get_user_reports(
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user reports with optional filters."""
    return await analytics_service.get_user_reports(
        db,
        current_user.id,
        report_type=report_type,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_update: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a report."""
    report = await analytics_service.update_report(
        db,
        report_id,
        report_update.dict(exclude_unset=True)
    )
    if not report or report.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("/reports/{report_id}/generate")
async def generate_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a report file."""
    report = await analytics_service.get_report(db, report_id)
    if not report or report.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    
    background_tasks.add_task(analytics_service.generate_report, db, report_id)
    return {"message": "Report generation started"}

# Metrics Endpoints
@router.post("/metrics", response_model=MetricResponse)
async def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new metric."""
    try:
        return await analytics_service.create_metric(
            db,
            metric.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/metrics/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: int,
    metric_data: MetricUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a metric."""
    try:
        return await analytics_service.update_metric(
            db,
            metric_id,
            metric_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics", response_model=List[MetricResponse])
async def get_metrics(
    metric_type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    time_period: Optional[str] = Query(None, description="Filter by time period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get metrics with optional filters."""
    return await analytics_service.get_metrics(
        db,
        metric_type=metric_type,
        time_period=time_period
    )

# Dashboards Endpoints
@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dashboard."""
    try:
        return await analytics_service.create_dashboard(
            db,
            current_user.id,
            dashboard.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a dashboard by ID."""
    dashboard = await analytics_service.get_dashboard(db, dashboard_id)
    if not dashboard or (not dashboard.is_public and dashboard.created_by != current_user.id):
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

@router.get("/dashboards", response_model=List[DashboardResponse])
async def get_user_dashboards(
    dashboard_type: Optional[DashboardType] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user dashboards."""
    return await analytics_service.get_user_dashboards(
        db,
        current_user.id,
        dashboard_type=dashboard_type,
        is_public=is_public
    )

@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: int,
    dashboard_update: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a dashboard."""
    dashboard = await analytics_service.update_dashboard(
        db,
        dashboard_id,
        current_user.id,
        dashboard_update.dict(exclude_unset=True)
    )
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard

# Widgets Endpoints
@router.post("/widgets", response_model=WidgetResponse)
async def create_widget(
    widget: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new widget."""
    try:
        return await analytics_service.create_widget(
            db,
            widget.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/widgets/{widget_id}", response_model=WidgetResponse)
async def get_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a widget by ID."""
    widget = await analytics_service.get_widget(db, widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

@router.get("/dashboards/{dashboard_id}/widgets", response_model=List[WidgetResponse])
async def get_dashboard_widgets(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all widgets for a dashboard."""
    return await analytics_service.get_dashboard_widgets(db, dashboard_id)

@router.put("/widgets/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: int,
    widget_update: WidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a widget."""
    widget = await analytics_service.update_widget(
        db,
        widget_id,
        widget_update.dict(exclude_unset=True)
    )
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

# Exports Endpoints
@router.post("/exports", response_model=AnalyticsExportResponse)
async def create_export(
    export: AnalyticsExportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new data export."""
    try:
        return await analytics_service.create_export(
            db,
            current_user.id,
            export.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/exports/{export_id}", response_model=AnalyticsExportResponse)
async def get_export(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get an export by ID."""
    export = await analytics_service.get_export(db, export_id)
    if not export or export.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Export not found")
    return export

@router.get("/exports", response_model=List[AnalyticsExportResponse])
async def get_user_exports(
    format: Optional[ReportFormat] = Query(None, description="Filter by format"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user exports with optional filters."""
    return await analytics_service.get_user_exports(
        db,
        current_user.id,
        format=format,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.put("/exports/{export_id}", response_model=AnalyticsExportResponse)
async def update_export(
    export_id: int,
    export_update: AnalyticsExportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an export."""
    export = await analytics_service.update_export(
        db,
        export_id,
        current_user.id,
        export_update.dict(exclude_unset=True)
    )
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    return export

# Statistics Endpoint
@router.get("/stats", response_model=AnalyticsStats)
async def get_analytics_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive analytics statistics."""
    try:
        return await analytics_service.get_analytics_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/reports", response_model=ReportStats)
async def get_report_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get report statistics."""
    try:
        return await analytics_service.get_report_stats(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/metrics", response_model=MetricStats)
async def get_metric_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get metric statistics."""
    try:
        return await analytics_service.get_metric_stats()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/dashboards", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics."""
    try:
        return await analytics_service.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/alerts", response_model=AlertStats)
async def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert statistics."""
    try:
        return await analytics_service.get_alert_stats()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Alert Endpoints
@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new alert."""
    try:
        return await analytics_service.create_alert(
            db,
            alert.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an alert."""
    alert = await analytics_service.update_alert(
        db,
        alert_id,
        alert_update.dict(exclude_unset=True)
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert 