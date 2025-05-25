from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json

from ..models.chw import (
    CHW,
    CHWVisit,
    CHWAssignment,
    CHWPerformance,
    CHWTraining,
    VisitStatus,
    VisitType,
    CHWStatus
)
from ..schemas.chw import (
    CHWCreate,
    CHWUpdate,
    VisitCreate,
    VisitUpdate,
    AssignmentCreate,
    AssignmentUpdate,
    PerformanceCreate,
    TrainingCreate
)

class CHWService:
    def __init__(self):
        pass

    async def create_chw(self, db: Session, chw_data: Dict[str, Any]) -> CHW:
        """Create a new CHW."""
        chw = CHW(**chw_data)
        db.add(chw)
        db.commit()
        db.refresh(chw)
        return chw

    async def get_chw(self, db: Session, chw_id: int) -> Optional[CHW]:
        """Get a CHW by ID."""
        return db.query(CHW).filter(CHW.id == chw_id).first()

    async def update_chw(self, db: Session, chw_id: int, chw_data: Dict[str, Any]) -> Optional[CHW]:
        """Update a CHW's information."""
        chw = await self.get_chw(db, chw_id)
        if not chw:
            return None

        for key, value in chw_data.items():
            setattr(chw, key, value)

        db.commit()
        db.refresh(chw)
        return chw

    async def create_visit(self, db: Session, visit_data: Dict[str, Any]) -> CHWVisit:
        """Create a new CHW visit."""
        visit = CHWVisit(**visit_data)
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit

    async def update_visit(self, db: Session, visit_id: int, visit_data: Dict[str, Any]) -> Optional[CHWVisit]:
        """Update a CHW visit."""
        visit = db.query(CHWVisit).filter(CHWVisit.id == visit_id).first()
        if not visit:
            return None

        for key, value in visit_data.items():
            setattr(visit, key, value)

        db.commit()
        db.refresh(visit)
        return visit

    async def get_visits(
        self,
        db: Session,
        chw_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status: Optional[VisitStatus] = None,
        visit_type: Optional[VisitType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CHWVisit]:
        """Get CHW visits with filters."""
        query = db.query(CHWVisit)

        if chw_id:
            query = query.filter(CHWVisit.chw_id == chw_id)
        if patient_id:
            query = query.filter(CHWVisit.patient_id == patient_id)
        if status:
            query = query.filter(CHWVisit.status == status)
        if visit_type:
            query = query.filter(CHWVisit.visit_type == visit_type)
        if start_date:
            query = query.filter(CHWVisit.scheduled_date >= start_date)
        if end_date:
            query = query.filter(CHWVisit.scheduled_date <= end_date)

        return query.all()

    async def create_assignment(self, db: Session, assignment_data: Dict[str, Any]) -> CHWAssignment:
        """Create a new CHW assignment."""
        assignment = CHWAssignment(**assignment_data)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    async def update_assignment(self, db: Session, assignment_id: int, assignment_data: Dict[str, Any]) -> Optional[CHWAssignment]:
        """Update a CHW assignment."""
        assignment = db.query(CHWAssignment).filter(CHWAssignment.id == assignment_id).first()
        if not assignment:
            return None

        for key, value in assignment_data.items():
            setattr(assignment, key, value)

        db.commit()
        db.refresh(assignment)
        return assignment

    async def get_assignments(
        self,
        db: Session,
        chw_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
        active_only: bool = True
    ) -> List[CHWAssignment]:
        """Get CHW assignments with filters."""
        query = db.query(CHWAssignment)

        if chw_id:
            query = query.filter(CHWAssignment.chw_id == chw_id)
        if patient_id:
            query = query.filter(CHWAssignment.patient_id == patient_id)
        if status:
            query = query.filter(CHWAssignment.status == status)
        if active_only:
            query = query.filter(
                or_(
                    CHWAssignment.end_date.is_(None),
                    CHWAssignment.end_date > datetime.utcnow()
                )
            )

        return query.all()

    async def create_performance(self, db: Session, performance_data: Dict[str, Any]) -> CHWPerformance:
        """Create new CHW performance metrics."""
        performance = CHWPerformance(**performance_data)
        db.add(performance)
        db.commit()
        db.refresh(performance)
        return performance

    async def update_performance(self, db: Session, performance_id: int, performance_data: Dict[str, Any]) -> Optional[CHWPerformance]:
        """Update CHW performance metrics."""
        performance = db.query(CHWPerformance).filter(CHWPerformance.id == performance_id).first()
        if not performance:
            return None

        for key, value in performance_data.items():
            setattr(performance, key, value)

        db.commit()
        db.refresh(performance)
        return performance

    async def get_performance(
        self,
        db: Session,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CHWPerformance]:
        """Get CHW performance metrics."""
        query = db.query(CHWPerformance).filter(CHWPerformance.chw_id == chw_id)

        if start_date:
            query = query.filter(CHWPerformance.metric_date >= start_date)
        if end_date:
            query = query.filter(CHWPerformance.metric_date <= end_date)

        return query.order_by(CHWPerformance.metric_date.desc()).all()

    async def create_training(self, db: Session, training_data: Dict[str, Any]) -> CHWTraining:
        """Create a new CHW training record."""
        training = CHWTraining(**training_data)
        db.add(training)
        db.commit()
        db.refresh(training)
        return training

    async def update_training(self, db: Session, training_id: int, training_data: Dict[str, Any]) -> Optional[CHWTraining]:
        """Update a CHW training record."""
        training = db.query(CHWTraining).filter(CHWTraining.id == training_id).first()
        if not training:
            return None

        for key, value in training_data.items():
            setattr(training, key, value)

        db.commit()
        db.refresh(training)
        return training

    async def get_training(
        self,
        db: Session,
        chw_id: int,
        status: Optional[str] = None,
        active_only: bool = True
    ) -> List[CHWTraining]:
        """Get CHW training records."""
        query = db.query(CHWTraining).filter(CHWTraining.chw_id == chw_id)

        if status:
            query = query.filter(CHWTraining.status == status)
        if active_only:
            query = query.filter(
                or_(
                    CHWTraining.expiry_date.is_(None),
                    CHWTraining.expiry_date > datetime.utcnow()
                )
            )

        return query.order_by(CHWTraining.start_date.desc()).all()

    async def get_chw_stats(
        self,
        db: Session,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive statistics for a CHW."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Get visit statistics
        visits = await self.get_visits(db, chw_id=chw_id, start_date=start_date, end_date=end_date)
        total_visits = len(visits)
        completed_visits = len([v for v in visits if v.status == VisitStatus.COMPLETED])
        pending_visits = len([v for v in visits if v.status in [VisitStatus.SCHEDULED, VisitStatus.IN_PROGRESS]])

        # Get performance metrics
        performance = await self.get_performance(db, chw_id, start_date, end_date)
        if performance:
            latest_performance = performance[0]
            average_response_time = latest_performance.average_response_time
            patient_satisfaction = latest_performance.patient_satisfaction
            compliance_rate = latest_performance.compliance_rate
        else:
            average_response_time = 0.0
            patient_satisfaction = 0.0
            compliance_rate = 0.0

        # Get recent and upcoming visits
        recent_visits = visits[:5]  # Last 5 visits
        upcoming_visits = [v for v in visits if v.status == VisitStatus.SCHEDULED][:5]  # Next 5 scheduled visits

        # Calculate performance trend
        performance_trend = {
            "visits_completed": [p.visits_completed for p in performance],
            "patient_satisfaction": [p.patient_satisfaction for p in performance if p.patient_satisfaction],
            "compliance_rate": [p.compliance_rate for p in performance if p.compliance_rate]
        }

        return {
            "total_visits": total_visits,
            "completed_visits": completed_visits,
            "pending_visits": pending_visits,
            "patients_served": len(set(v.patient_id for v in visits)),
            "average_response_time": average_response_time,
            "patient_satisfaction": patient_satisfaction,
            "compliance_rate": compliance_rate,
            "recent_visits": recent_visits,
            "upcoming_visits": upcoming_visits,
            "performance_trend": performance_trend
        }

# Create a singleton instance
chw_service = CHWService() 