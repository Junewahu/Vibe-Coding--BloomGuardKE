from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.incentives import Incentive, IncentiveRule, IncentivePayment
from ..models.analytics import (
    MessageDeliveryMetrics,
    NHIFClaimMetrics,
    PatientEngagementMetrics,
    FacilityPerformanceMetrics
)
from ..crud import incentives as incentive_crud
from ..schemas.incentives import (
    IncentiveCreate,
    IncentiveRuleCreate,
    IncentivePaymentCreate
)

class IncentiveService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_performance_incentive(
        self,
        facility_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Incentive]:
        """Calculate performance-based incentive for a user."""
        # Get performance metrics
        metrics = self.db.query(FacilityPerformanceMetrics).filter(
            FacilityPerformanceMetrics.facility_id == facility_id,
            FacilityPerformanceMetrics.date >= start_date,
            FacilityPerformanceMetrics.date <= end_date
        ).all()

        if not metrics:
            return None

        # Calculate total appointments and completion rate
        total_appointments = sum(m.total_appointments for m in metrics)
        completed_appointments = sum(m.completed_appointments for m in metrics)
        completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0

        # Get applicable incentive rule
        rule = self.db.query(IncentiveRule).filter(
            IncentiveRule.facility_id == facility_id,
            IncentiveRule.incentive_type == "performance",
            IncentiveRule.is_active == True,
            IncentiveRule.start_date <= end_date,
            IncentiveRule.end_date >= start_date
        ).first()

        if not rule:
            return None

        # Calculate incentive amount
        if completion_rate >= rule.target_value:
            bonus_multiplier = rule.bonus_multiplier
        else:
            bonus_multiplier = 1.0

        base_amount = rule.base_amount
        total_amount = base_amount * bonus_multiplier

        # Create incentive record
        incentive = IncentiveCreate(
            facility_id=facility_id,
            user_id=user_id,
            incentive_type="performance",
            period=rule.period,
            start_date=start_date,
            end_date=end_date,
            target_value=rule.target_value,
            achieved_value=completion_rate,
            base_amount=base_amount,
            bonus_amount=total_amount - base_amount,
            total_amount=total_amount,
            metrics={
                "total_appointments": total_appointments,
                "completed_appointments": completed_appointments,
                "completion_rate": completion_rate
            }
        )

        return incentive_crud.create_incentive(self.db, incentive)

    def calculate_attendance_incentive(
        self,
        facility_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Incentive]:
        """Calculate attendance-based incentive for a user."""
        # Get attendance metrics (this would need to be implemented in your system)
        # For now, we'll use a placeholder
        attendance_rate = 95.0  # This should come from your attendance tracking system

        # Get applicable incentive rule
        rule = self.db.query(IncentiveRule).filter(
            IncentiveRule.facility_id == facility_id,
            IncentiveRule.incentive_type == "attendance",
            IncentiveRule.is_active == True,
            IncentiveRule.start_date <= end_date,
            IncentiveRule.end_date >= start_date
        ).first()

        if not rule:
            return None

        # Calculate incentive amount
        if attendance_rate >= rule.target_value:
            bonus_multiplier = rule.bonus_multiplier
        else:
            bonus_multiplier = 1.0

        base_amount = rule.base_amount
        total_amount = base_amount * bonus_multiplier

        # Create incentive record
        incentive = IncentiveCreate(
            facility_id=facility_id,
            user_id=user_id,
            incentive_type="attendance",
            period=rule.period,
            start_date=start_date,
            end_date=end_date,
            target_value=rule.target_value,
            achieved_value=attendance_rate,
            base_amount=base_amount,
            bonus_amount=total_amount - base_amount,
            total_amount=total_amount,
            metrics={"attendance_rate": attendance_rate}
        )

        return incentive_crud.create_incentive(self.db, incentive)

    def calculate_patient_satisfaction_incentive(
        self,
        facility_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Incentive]:
        """Calculate patient satisfaction-based incentive for a user."""
        # Get patient satisfaction metrics
        metrics = self.db.query(PatientEngagementMetrics).filter(
            PatientEngagementMetrics.facility_id == facility_id,
            PatientEngagementMetrics.date >= start_date,
            PatientEngagementMetrics.date <= end_date
        ).all()

        if not metrics:
            return None

        # Calculate average satisfaction score
        total_score = sum(m.patient_satisfaction_score for m in metrics)
        avg_satisfaction = total_score / len(metrics)

        # Get applicable incentive rule
        rule = self.db.query(IncentiveRule).filter(
            IncentiveRule.facility_id == facility_id,
            IncentiveRule.incentive_type == "patient_satisfaction",
            IncentiveRule.is_active == True,
            IncentiveRule.start_date <= end_date,
            IncentiveRule.end_date >= start_date
        ).first()

        if not rule:
            return None

        # Calculate incentive amount
        if avg_satisfaction >= rule.target_value:
            bonus_multiplier = rule.bonus_multiplier
        else:
            bonus_multiplier = 1.0

        base_amount = rule.base_amount
        total_amount = base_amount * bonus_multiplier

        # Create incentive record
        incentive = IncentiveCreate(
            facility_id=facility_id,
            user_id=user_id,
            incentive_type="patient_satisfaction",
            period=rule.period,
            start_date=start_date,
            end_date=end_date,
            target_value=rule.target_value,
            achieved_value=avg_satisfaction,
            base_amount=base_amount,
            bonus_amount=total_amount - base_amount,
            total_amount=total_amount,
            metrics={"average_satisfaction": avg_satisfaction}
        )

        return incentive_crud.create_incentive(self.db, incentive)

    def calculate_quality_care_incentive(
        self,
        facility_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Incentive]:
        """Calculate quality care-based incentive for a user."""
        # Get NHIF claim metrics
        metrics = self.db.query(NHIFClaimMetrics).filter(
            NHIFClaimMetrics.facility_id == facility_id,
            NHIFClaimMetrics.date >= start_date,
            NHIFClaimMetrics.date <= end_date
        ).all()

        if not metrics:
            return None

        # Calculate claim approval rate
        total_claims = sum(m.total_claims for m in metrics)
        approved_claims = sum(m.approved_claims for m in metrics)
        approval_rate = (approved_claims / total_claims * 100) if total_claims > 0 else 0

        # Get applicable incentive rule
        rule = self.db.query(IncentiveRule).filter(
            IncentiveRule.facility_id == facility_id,
            IncentiveRule.incentive_type == "quality_care",
            IncentiveRule.is_active == True,
            IncentiveRule.start_date <= end_date,
            IncentiveRule.end_date >= start_date
        ).first()

        if not rule:
            return None

        # Calculate incentive amount
        if approval_rate >= rule.target_value:
            bonus_multiplier = rule.bonus_multiplier
        else:
            bonus_multiplier = 1.0

        base_amount = rule.base_amount
        total_amount = base_amount * bonus_multiplier

        # Create incentive record
        incentive = IncentiveCreate(
            facility_id=facility_id,
            user_id=user_id,
            incentive_type="quality_care",
            period=rule.period,
            start_date=start_date,
            end_date=end_date,
            target_value=rule.target_value,
            achieved_value=approval_rate,
            base_amount=base_amount,
            bonus_amount=total_amount - base_amount,
            total_amount=total_amount,
            metrics={
                "total_claims": total_claims,
                "approved_claims": approved_claims,
                "approval_rate": approval_rate
            }
        )

        return incentive_crud.create_incentive(self.db, incentive)

    def process_incentive_payment(
        self,
        incentive_id: int,
        payment_date: datetime,
        payment_method: str,
        payment_reference: str,
        notes: Optional[str] = None
    ) -> Optional[IncentivePayment]:
        """Process payment for an approved incentive."""
        incentive = incentive_crud.get_incentive(self.db, incentive_id)
        if not incentive or incentive.status != "approved":
            return None

        payment = IncentivePaymentCreate(
            incentive_id=incentive_id,
            amount=incentive.total_amount,
            payment_date=payment_date,
            payment_method=payment_method,
            payment_reference=payment_reference,
            status="completed",
            notes=notes
        )

        return incentive_crud.create_incentive_payment(self.db, payment)

    def get_incentive_summary(
        self,
        facility_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get summary of incentives for a facility."""
        return incentive_crud.get_incentive_summary(
            self.db,
            facility_id,
            start_date,
            end_date
        )

    def get_user_incentive_summary(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get summary of incentives for a user."""
        return incentive_crud.get_user_incentive_summary(
            self.db,
            user_id,
            start_date,
            end_date
        ) 