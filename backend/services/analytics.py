from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import json
import os
import pandas as pd
from ..models.analytics import (
    Report, Metric, Dashboard, DashboardWidget, Export,
    ReportType, ReportFormat, ReportStatus,
    MetricType, DashboardType, Widget, Alert
)
from ..schemas.analytics import (
    ReportCreate, ReportUpdate,
    MetricCreate, MetricUpdate,
    DashboardCreate, DashboardUpdate,
    DashboardWidgetCreate, DashboardWidgetUpdate,
    ExportCreate, ExportUpdate,
    WidgetCreate, WidgetUpdate,
    AlertCreate, AlertUpdate,
    ReportStats, MetricStats, DashboardStats, AlertStats
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    # Report Management
    async def create_report(self, report_data: ReportCreate, user_id: int) -> Report:
        """Create a new report."""
        try:
            report = Report(
                **report_data.dict(),
                generated_by=user_id,
                status="pending"
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            # Generate report data asynchronously
            await self._generate_report_data(report)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating report: {str(e)}")
            raise

    async def update_report(self, report_id: int, report_data: ReportUpdate) -> Report:
        """Update a report."""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ValueError("Report not found")

            for key, value in report_data.dict(exclude_unset=True).items():
                setattr(report, key, value)

            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating report: {str(e)}")
            raise

    async def get_reports(
        self,
        user_id: int,
        report_type: Optional[ReportType] = None,
        status: Optional[str] = None
    ) -> List[Report]:
        """Get reports with optional filters."""
        try:
            query = self.db.query(Report).filter(Report.generated_by == user_id)

            if report_type:
                query = query.filter(Report.report_type == report_type)
            if status:
                query = query.filter(Report.status == status)

            return query.order_by(desc(Report.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting reports: {str(e)}")
            raise

    # Metric Management
    async def create_metric(self, metric_data: MetricCreate) -> Metric:
        """Create a new metric."""
        try:
            metric = Metric(**metric_data.dict())
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            return metric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating metric: {str(e)}")
            raise

    async def update_metric(self, metric_id: int, metric_data: MetricUpdate) -> Metric:
        """Update a metric."""
        try:
            metric = self.db.query(Metric).filter(Metric.id == metric_id).first()
            if not metric:
                raise ValueError("Metric not found")

            for key, value in metric_data.dict(exclude_unset=True).items():
                setattr(metric, key, value)

            self.db.commit()
            self.db.refresh(metric)
            return metric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating metric: {str(e)}")
            raise

    async def get_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        time_period: Optional[str] = None
    ) -> List[Metric]:
        """Get metrics with optional filters."""
        try:
            query = self.db.query(Metric)

            if metric_type:
                query = query.filter(Metric.metric_type == metric_type)
            if time_period:
                query = query.filter(Metric.time_period == time_period)

            return query.order_by(desc(Metric.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise

    # Dashboard Management
    async def create_dashboard(self, dashboard_data: DashboardCreate, user_id: int) -> Dashboard:
        """Create a new dashboard."""
        try:
            dashboard = Dashboard(**dashboard_data.dict(), user_id=user_id)
            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)
            return dashboard
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating dashboard: {str(e)}")
            raise

    async def update_dashboard(
        self,
        dashboard_id: int,
        dashboard_data: DashboardUpdate
    ) -> Dashboard:
        """Update a dashboard."""
        try:
            dashboard = self.db.query(Dashboard).filter(
                Dashboard.id == dashboard_id
            ).first()
            if not dashboard:
                raise ValueError("Dashboard not found")

            for key, value in dashboard_data.dict(exclude_unset=True).items():
                setattr(dashboard, key, value)

            self.db.commit()
            self.db.refresh(dashboard)
            return dashboard
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating dashboard: {str(e)}")
            raise

    async def get_dashboards(
        self,
        user_id: int,
        is_public: Optional[bool] = None
    ) -> List[Dashboard]:
        """Get dashboards with optional filters."""
        try:
            query = self.db.query(Dashboard).filter(
                or_(
                    Dashboard.user_id == user_id,
                    Dashboard.is_public == True
                )
            )

            if is_public is not None:
                query = query.filter(Dashboard.is_public == is_public)

            return query.order_by(desc(Dashboard.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting dashboards: {str(e)}")
            raise

    # Widget Management
    async def create_widget(self, widget_data: WidgetCreate) -> Widget:
        """Create a new widget."""
        try:
            widget = Widget(**widget_data.dict())
            self.db.add(widget)
            self.db.commit()
            self.db.refresh(widget)
            return widget
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating widget: {str(e)}")
            raise

    async def update_widget(self, widget_id: int, widget_data: WidgetUpdate) -> Widget:
        """Update a widget."""
        try:
            widget = self.db.query(Widget).filter(Widget.id == widget_id).first()
            if not widget:
                raise ValueError("Widget not found")

            for key, value in widget_data.dict(exclude_unset=True).items():
                setattr(widget, key, value)

            self.db.commit()
            self.db.refresh(widget)
            return widget
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating widget: {str(e)}")
            raise

    # Alert Management
    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert."""
        try:
            alert = Alert(**alert_data.dict())
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating alert: {str(e)}")
            raise

    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Alert:
        """Update an alert."""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise ValueError("Alert not found")

            for key, value in alert_data.dict(exclude_unset=True).items():
                setattr(alert, key, value)

            self.db.commit()
            self.db.refresh(alert)
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating alert: {str(e)}")
            raise

    # Statistics
    async def get_report_stats(self, user_id: int) -> ReportStats:
        """Get report statistics."""
        try:
            reports = self.db.query(Report).filter(
                Report.generated_by == user_id
            ).all()
            
            total_reports = len(reports)
            reports_by_type = {}
            total_generation_time = 0
            successful_reports = 0

            for report in reports:
                # Count by type
                report_type = report.report_type.value
                reports_by_type[report_type] = reports_by_type.get(report_type, 0) + 1

                # Calculate generation time
                if report.status == "completed":
                    generation_time = (
                        report.updated_at - report.created_at
                    ).total_seconds()
                    total_generation_time += generation_time
                    successful_reports += 1

            return ReportStats(
                total_reports=total_reports,
                reports_by_type=reports_by_type,
                average_generation_time=total_generation_time / successful_reports
                if successful_reports > 0 else 0,
                success_rate=successful_reports / total_reports if total_reports > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting report stats: {str(e)}")
            raise

    async def get_metric_stats(self) -> MetricStats:
        """Get metric statistics."""
        try:
            metrics = self.db.query(Metric).all()
            
            total_metrics = len(metrics)
            metrics_by_type = {}
            total_value = 0
            total_updates = 0

            for metric in metrics:
                # Count by type
                metric_type = metric.metric_type.value
                metrics_by_type[metric_type] = metrics_by_type.get(metric_type, 0) + 1

                # Calculate average value
                if metric.value is not None:
                    total_value += metric.value

                # Calculate update frequency
                if metric.updated_at:
                    update_time = (
                        metric.updated_at - metric.created_at
                    ).total_seconds() / 3600  # Convert to hours
                    total_updates += update_time

            return MetricStats(
                total_metrics=total_metrics,
                metrics_by_type=metrics_by_type,
                average_value=total_value / total_metrics if total_metrics > 0 else 0,
                update_frequency=total_updates / total_metrics if total_metrics > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting metric stats: {str(e)}")
            raise

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics."""
        try:
            dashboards = self.db.query(Dashboard).all()
            
            total_dashboards = len(dashboards)
            public_dashboards = len([d for d in dashboards if d.is_public])
            total_widgets = sum(len(d.widgets) for d in dashboards)
            widget_types = {}

            for dashboard in dashboards:
                for widget in dashboard.widgets:
                    widget_type = widget["widget_type"]
                    widget_types[widget_type] = widget_types.get(widget_type, 0) + 1

            return DashboardStats(
                total_dashboards=total_dashboards,
                public_dashboards=public_dashboards,
                average_widgets=total_widgets / total_dashboards if total_dashboards > 0 else 0,
                most_used_widgets=widget_types
            )
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise

    async def get_alert_stats(self) -> AlertStats:
        """Get alert statistics."""
        try:
            alerts = self.db.query(Alert).all()
            
            total_alerts = len(alerts)
            active_alerts = len([a for a in alerts if a.is_active])
            alerts_by_severity = {}
            total_response_time = 0
            responded_alerts = 0

            for alert in alerts:
                # Count by severity
                severity = alert.severity
                alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1

                # Calculate response time
                if alert.last_triggered:
                    response_time = (
                        alert.last_triggered - alert.created_at
                    ).total_seconds() / 3600  # Convert to hours
                    total_response_time += response_time
                    responded_alerts += 1

            return AlertStats(
                total_alerts=total_alerts,
                active_alerts=active_alerts,
                alerts_by_severity=alerts_by_severity,
                average_response_time=total_response_time / responded_alerts
                if responded_alerts > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting alert stats: {str(e)}")
            raise

    # Helper Methods
    async def _generate_report_data(self, report: Report) -> None:
        """Generate report data asynchronously."""
        try:
            # Update report status
            report.status = "processing"
            self.db.commit()

            # Generate report data based on type
            if report.report_type == ReportType.PATIENT_HEALTH:
                data = await self._generate_patient_health_report(report)
            elif report.report_type == ReportType.CHW_PERFORMANCE:
                data = await self._generate_chw_performance_report(report)
            elif report.report_type == ReportType.ADHERENCE:
                data = await self._generate_adherence_report(report)
            elif report.report_type == ReportType.RESOURCE_UTILIZATION:
                data = await self._generate_resource_utilization_report(report)
            elif report.report_type == ReportType.PROGRAM_EFFECTIVENESS:
                data = await self._generate_program_effectiveness_report(report)
            else:
                data = await self._generate_custom_report(report)

            # Update report with generated data
            report.data = data
            report.status = "completed"
            self.db.commit()
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)
            self.db.commit()
            logger.error(f"Error generating report data: {str(e)}")
            raise

    async def _generate_patient_health_report(self, report: Report) -> Dict[str, Any]:
        """Generate patient health report data."""
        # Implementation depends on specific requirements
        return {}

    async def _generate_chw_performance_report(self, report: Report) -> Dict[str, Any]:
        """Generate CHW performance report data."""
        # Implementation depends on specific requirements
        return {}

    async def _generate_adherence_report(self, report: Report) -> Dict[str, Any]:
        """Generate adherence report data."""
        # Implementation depends on specific requirements
        return {}

    async def _generate_resource_utilization_report(self, report: Report) -> Dict[str, Any]:
        """Generate resource utilization report data."""
        # Implementation depends on specific requirements
        return {}

    async def _generate_program_effectiveness_report(self, report: Report) -> Dict[str, Any]:
        """Generate program effectiveness report data."""
        # Implementation depends on specific requirements
        return {}

    async def _generate_custom_report(self, report: Report) -> Dict[str, Any]:
        """Generate custom report data."""
        # Implementation depends on specific requirements
        return {}

# Create singleton instance
analytics_service = AnalyticsService() 