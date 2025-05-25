from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.patient import Patient
from ..services.portal import portal_service
from ..schemas.portal import (
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse,
    PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse,
    HealthMetricCreate, HealthMetricUpdate, HealthMetricResponse,
    PortalMessageCreate, PortalMessageUpdate, PortalMessageResponse,
    PortalNotificationCreate, PortalNotificationUpdate, PortalNotificationResponse,
    PatientPortalStats
)
from ..models.portal import MedicalRecordType, PrescriptionStatus, HealthMetricType, MessageType

router = APIRouter(prefix="/portal", tags=["portal"])

# Medical Records Endpoints
@router.post("/records", response_model=MedicalRecordResponse)
async def create_medical_record(
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new medical record."""
    try:
        return await portal_service.create_medical_record(
            db,
            record.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a medical record by ID."""
    record = await portal_service.get_medical_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record

@router.get("/records", response_model=List[MedicalRecordResponse])
async def get_patient_records(
    patient_id: int,
    record_type: Optional[MedicalRecordType] = Query(None, description="Filter by record type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient medical records with optional filters."""
    return await portal_service.get_patient_records(
        db,
        patient_id,
        record_type=record_type,
        start_date=start_date,
        end_date=end_date
    )

@router.put("/records/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_update: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a medical record."""
    record = await portal_service.update_medical_record(
        db,
        record_id,
        record_update.dict(exclude_unset=True)
    )
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record

# Prescriptions Endpoints
@router.post("/prescriptions", response_model=PrescriptionResponse)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new prescription."""
    try:
        return await portal_service.create_prescription(
            db,
            prescription.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a prescription by ID."""
    prescription = await portal_service.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.get("/prescriptions", response_model=List[PrescriptionResponse])
async def get_patient_prescriptions(
    patient_id: int,
    status: Optional[PrescriptionStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient prescriptions with optional status filter."""
    return await portal_service.get_patient_prescriptions(
        db,
        patient_id,
        status=status
    )

@router.put("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: int,
    prescription_update: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a prescription."""
    prescription = await portal_service.update_prescription(
        db,
        prescription_id,
        prescription_update.dict(exclude_unset=True)
    )
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

# Health Metrics Endpoints
@router.post("/metrics", response_model=HealthMetricResponse)
async def create_health_metric(
    metric: HealthMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new health metric."""
    try:
        return await portal_service.create_health_metric(
            db,
            metric.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics", response_model=List[HealthMetricResponse])
async def get_health_metrics(
    patient_id: int,
    metric_type: Optional[HealthMetricType] = Query(None, description="Filter by metric type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient health metrics with optional filters."""
    return await portal_service.get_health_metrics(
        db,
        patient_id,
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date
    )

# Messages Endpoints
@router.post("/messages", response_model=PortalMessageResponse)
async def create_message(
    message: PortalMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new portal message."""
    try:
        return await portal_service.create_portal_message(
            db,
            message.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages", response_model=List[PortalMessageResponse])
async def get_messages(
    patient_id: int,
    message_type: Optional[MessageType] = Query(None, description="Filter by message type"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient messages with optional filters."""
    return await portal_service.get_messages(
        db,
        patient_id,
        message_type=message_type,
        is_read=is_read,
        limit=limit
    )

@router.put("/messages/{message_id}", response_model=PortalMessageResponse)
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a message as read."""
    message = await portal_service.mark_message_read(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

# Notifications Endpoints
@router.post("/notifications", response_model=PortalNotificationResponse)
async def create_notification(
    notification: PortalNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new portal notification."""
    try:
        return await portal_service.create_notification(
            db,
            notification.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/notifications", response_model=List[PortalNotificationResponse])
async def get_notifications(
    patient_id: int,
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient notifications with optional read status filter."""
    return await portal_service.get_notifications(
        db,
        patient_id,
        is_read=is_read,
        limit=limit
    )

@router.put("/notifications/{notification_id}", response_model=PortalNotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    notification = await portal_service.mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# Statistics Endpoint
@router.get("/stats", response_model=PatientPortalStats)
async def get_portal_stats(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive portal statistics for a patient."""
    try:
        return await portal_service.get_portal_stats(db, patient_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 