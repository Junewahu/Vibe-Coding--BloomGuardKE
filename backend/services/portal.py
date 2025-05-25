from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from ..models.portal import (
    MedicalRecord, Prescription, HealthMetric,
    PortalMessage, PortalNotification, MedicalRecordType,
    PrescriptionStatus, HealthMetricType, MessageType
)
from ..models.appointment import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)

class PortalService:
    async def create_medical_record(
        self,
        db: Session,
        record_data: Dict[str, Any]
    ) -> MedicalRecord:
        """Create a new medical record."""
        record = MedicalRecord(**record_data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    async def get_medical_record(
        self,
        db: Session,
        record_id: int
    ) -> Optional[MedicalRecord]:
        """Get a medical record by ID."""
        return db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()

    async def get_patient_records(
        self,
        db: Session,
        patient_id: int,
        record_type: Optional[MedicalRecordType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MedicalRecord]:
        """Get patient medical records with optional filters."""
        query = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id)
        
        if record_type:
            query = query.filter(MedicalRecord.record_type == record_type)
        if start_date:
            query = query.filter(MedicalRecord.created_at >= start_date)
        if end_date:
            query = query.filter(MedicalRecord.created_at <= end_date)
        
        return query.order_by(MedicalRecord.created_at.desc()).all()

    async def update_medical_record(
        self,
        db: Session,
        record_id: int,
        record_data: Dict[str, Any]
    ) -> Optional[MedicalRecord]:
        """Update a medical record."""
        record = await self.get_medical_record(db, record_id)
        if not record:
            return None

        for key, value in record_data.items():
            setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record

    async def create_prescription(
        self,
        db: Session,
        prescription_data: Dict[str, Any]
    ) -> Prescription:
        """Create a new prescription."""
        prescription = Prescription(**prescription_data)
        db.add(prescription)
        db.commit()
        db.refresh(prescription)
        return prescription

    async def get_prescription(
        self,
        db: Session,
        prescription_id: int
    ) -> Optional[Prescription]:
        """Get a prescription by ID."""
        return db.query(Prescription).filter(Prescription.id == prescription_id).first()

    async def get_patient_prescriptions(
        self,
        db: Session,
        patient_id: int,
        status: Optional[PrescriptionStatus] = None
    ) -> List[Prescription]:
        """Get patient prescriptions with optional status filter."""
        query = db.query(Prescription).filter(Prescription.patient_id == patient_id)
        
        if status:
            query = query.filter(Prescription.status == status)
        
        return query.order_by(Prescription.start_date.desc()).all()

    async def update_prescription(
        self,
        db: Session,
        prescription_id: int,
        prescription_data: Dict[str, Any]
    ) -> Optional[Prescription]:
        """Update a prescription."""
        prescription = await self.get_prescription(db, prescription_id)
        if not prescription:
            return None

        for key, value in prescription_data.items():
            setattr(prescription, key, value)

        db.commit()
        db.refresh(prescription)
        return prescription

    async def create_health_metric(
        self,
        db: Session,
        metric_data: Dict[str, Any]
    ) -> HealthMetric:
        """Create a new health metric."""
        metric = HealthMetric(**metric_data)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    async def get_health_metrics(
        self,
        db: Session,
        patient_id: int,
        metric_type: Optional[HealthMetricType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HealthMetric]:
        """Get patient health metrics with optional filters."""
        query = db.query(HealthMetric).filter(HealthMetric.patient_id == patient_id)
        
        if metric_type:
            query = query.filter(HealthMetric.metric_type == metric_type)
        if start_date:
            query = query.filter(HealthMetric.recorded_at >= start_date)
        if end_date:
            query = query.filter(HealthMetric.recorded_at <= end_date)
        
        return query.order_by(HealthMetric.recorded_at.desc()).all()

    async def create_portal_message(
        self,
        db: Session,
        message_data: Dict[str, Any]
    ) -> PortalMessage:
        """Create a new portal message."""
        message = PortalMessage(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    async def get_messages(
        self,
        db: Session,
        patient_id: int,
        message_type: Optional[MessageType] = None,
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[PortalMessage]:
        """Get patient messages with optional filters."""
        query = db.query(PortalMessage).filter(PortalMessage.patient_id == patient_id)
        
        if message_type:
            query = query.filter(PortalMessage.message_type == message_type)
        if is_read is not None:
            query = query.filter(PortalMessage.is_read == is_read)
        
        return query.order_by(PortalMessage.created_at.desc()).limit(limit).all()

    async def mark_message_read(
        self,
        db: Session,
        message_id: int
    ) -> Optional[PortalMessage]:
        """Mark a message as read."""
        message = db.query(PortalMessage).filter(PortalMessage.id == message_id).first()
        if not message:
            return None

        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
        return message

    async def create_notification(
        self,
        db: Session,
        notification_data: Dict[str, Any]
    ) -> PortalNotification:
        """Create a new portal notification."""
        notification = PortalNotification(**notification_data)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    async def get_notifications(
        self,
        db: Session,
        patient_id: int,
        is_read: Optional[bool] = None,
        limit: int = 20
    ) -> List[PortalNotification]:
        """Get patient notifications with optional read status filter."""
        query = db.query(PortalNotification).filter(PortalNotification.patient_id == patient_id)
        
        if is_read is not None:
            query = query.filter(PortalNotification.is_read == is_read)
        
        return query.order_by(PortalNotification.created_at.desc()).limit(limit).all()

    async def mark_notification_read(
        self,
        db: Session,
        notification_id: int
    ) -> Optional[PortalNotification]:
        """Mark a notification as read."""
        notification = db.query(PortalNotification).filter(PortalNotification.id == notification_id).first()
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        return notification

    async def get_portal_stats(
        self,
        db: Session,
        patient_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive portal statistics for a patient."""
        # Get total records
        total_records = db.query(MedicalRecord)\
            .filter(MedicalRecord.patient_id == patient_id)\
            .count()

        # Get active prescriptions
        active_prescriptions = db.query(Prescription)\
            .filter(
                and_(
                    Prescription.patient_id == patient_id,
                    Prescription.status == PrescriptionStatus.ACTIVE
                )
            )\
            .count()

        # Get recent health metrics
        recent_metrics = await self.get_health_metrics(
            db,
            patient_id,
            start_date=datetime.utcnow() - timedelta(days=7)
        )

        # Get unread messages
        unread_messages = db.query(PortalMessage)\
            .filter(
                and_(
                    PortalMessage.patient_id == patient_id,
                    PortalMessage.is_read == False
                )
            )\
            .count()

        # Get unread notifications
        unread_notifications = db.query(PortalNotification)\
            .filter(
                and_(
                    PortalNotification.patient_id == patient_id,
                    PortalNotification.is_read == False
                )
            )\
            .count()

        # Get upcoming appointments
        upcoming_appointments = db.query(Appointment)\
            .filter(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.status == AppointmentStatus.SCHEDULED,
                    Appointment.scheduled_time >= datetime.utcnow()
                )
            )\
            .count()

        # Get recent records
        recent_records = await self.get_patient_records(
            db,
            patient_id,
            start_date=datetime.utcnow() - timedelta(days=30)
        )

        # Get recent prescriptions
        recent_prescriptions = await self.get_patient_prescriptions(
            db,
            patient_id
        )

        return {
            "total_records": total_records,
            "active_prescriptions": active_prescriptions,
            "recent_health_metrics": recent_metrics,
            "unread_messages": unread_messages,
            "unread_notifications": unread_notifications,
            "upcoming_appointments": upcoming_appointments,
            "recent_records": recent_records,
            "recent_prescriptions": recent_prescriptions
        }

# Create singleton instance
portal_service = PortalService() 