from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.notification import Notification, NotificationTemplate
from ..models.patient import Patient
from ..models.scheduling import FollowUpSchedule, ScheduleStatus
from ..schemas.notification import NotificationCreate
from ..schemas.scheduling import FollowUpScheduleCreate
import json

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self, db: Session):
        self.db = db
        self.escalation_rules = self._load_escalation_rules()

    def _load_escalation_rules(self) -> Dict[str, Any]:
        """Load escalation rules from configuration"""
        return {
            "missed_appointment": {
                "thresholds": [
                    {
                        "attempts": 1,
                        "delay_hours": 24,
                        "channels": ["sms", "whatsapp"],
                        "priority": "high"
                    },
                    {
                        "attempts": 2,
                        "delay_hours": 48,
                        "channels": ["sms", "whatsapp", "ivr"],
                        "priority": "high"
                    },
                    {
                        "attempts": 3,
                        "delay_hours": 72,
                        "channels": ["sms", "whatsapp", "ivr", "ussd"],
                        "priority": "urgent",
                        "notify_staff": True
                    }
                ]
            },
            "medication_adherence": {
                "thresholds": [
                    {
                        "missed_doses": 1,
                        "delay_hours": 12,
                        "channels": ["sms", "whatsapp"],
                        "priority": "medium"
                    },
                    {
                        "missed_doses": 2,
                        "delay_hours": 24,
                        "channels": ["sms", "whatsapp", "ivr"],
                        "priority": "high"
                    },
                    {
                        "missed_doses": 3,
                        "delay_hours": 48,
                        "channels": ["sms", "whatsapp", "ivr", "ussd"],
                        "priority": "urgent",
                        "notify_staff": True
                    }
                ]
            },
            "test_results": {
                "thresholds": [
                    {
                        "delay_hours": 24,
                        "channels": ["sms", "whatsapp"],
                        "priority": "high"
                    },
                    {
                        "delay_hours": 48,
                        "channels": ["sms", "whatsapp", "ivr"],
                        "priority": "urgent",
                        "notify_staff": True
                    }
                ]
            },
            "emergency": {
                "thresholds": [
                    {
                        "delay_hours": 0,
                        "channels": ["sms", "whatsapp", "ivr"],
                        "priority": "urgent",
                        "notify_staff": True,
                        "notify_emergency": True
                    }
                ]
            }
        }

    async def check_escalations(self) -> None:
        """Check for cases that need escalation"""
        try:
            # Check missed appointments
            await self._check_missed_appointments()
            
            # Check medication adherence
            await self._check_medication_adherence()
            
            # Check pending test results
            await self._check_test_results()
            
            # Check emergency cases
            await self._check_emergency_cases()
        except Exception as e:
            logger.error(f"Error checking escalations: {str(e)}")
            raise

    async def _check_missed_appointments(self) -> None:
        """Check for missed appointments"""
        try:
            # Get missed appointments
            missed_appointments = self.db.query(FollowUpSchedule)\
                .filter(FollowUpSchedule.status == ScheduleStatus.PENDING)\
                .filter(FollowUpSchedule.start_date < datetime.utcnow())\
                .all()
            
            for appointment in missed_appointments:
                # Get notification attempts
                attempts = self.db.query(Notification)\
                    .filter(Notification.patient_id == appointment.patient_id)\
                    .filter(Notification.metadata["appointment_id"].astext == appointment.id)\
                    .filter(Notification.metadata["type"].astext == "missed_appointment")\
                    .count()
                
                # Get applicable escalation rule
                rule = next(
                    (r for r in self.escalation_rules["missed_appointment"]["thresholds"]
                     if r["attempts"] == attempts + 1),
                    None
                )
                
                if rule:
                    # Create escalation notification
                    await self._create_escalation_notification(
                        appointment.patient_id,
                        "missed_appointment",
                        rule,
                        {
                            "appointment_id": appointment.id,
                            "appointment_date": appointment.start_date.isoformat(),
                            "attempt": attempts + 1
                        }
                    )
        except Exception as e:
            logger.error(f"Error checking missed appointments: {str(e)}")
            raise

    async def _check_medication_adherence(self) -> None:
        """Check for medication adherence issues"""
        try:
            # TODO: Implement medication adherence tracking
            # This would involve checking medication logs and comparing against prescribed schedules
            pass
        except Exception as e:
            logger.error(f"Error checking medication adherence: {str(e)}")
            raise

    async def _check_test_results(self) -> None:
        """Check for pending test results"""
        try:
            # TODO: Implement test results tracking
            # This would involve checking test orders and their status
            pass
        except Exception as e:
            logger.error(f"Error checking test results: {str(e)}")
            raise

    async def _check_emergency_cases(self) -> None:
        """Check for emergency cases"""
        try:
            # Get emergency notifications
            emergency_notifications = self.db.query(Notification)\
                .filter(Notification.metadata["type"].astext == "emergency")\
                .filter(Notification.status == "pending")\
                .all()
            
            for notification in emergency_notifications:
                # Get escalation rule
                rule = self.escalation_rules["emergency"]["thresholds"][0]
                
                # Create escalation notification
                await self._create_escalation_notification(
                    notification.patient_id,
                    "emergency",
                    rule,
                    {
                        "notification_id": notification.id,
                        "message": notification.message
                    }
                )
        except Exception as e:
            logger.error(f"Error checking emergency cases: {str(e)}")
            raise

    async def _create_escalation_notification(
        self,
        patient_id: str,
        escalation_type: str,
        rule: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Create escalation notification"""
        try:
            # Get patient
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                logger.error(f"Patient not found: {patient_id}")
                return
            
            # Get notification template
            template = self.db.query(NotificationTemplate)\
                .filter(NotificationTemplate.type == escalation_type)\
                .filter(NotificationTemplate.is_active == True)\
                .first()
            
            if not template:
                logger.error(f"Template not found for type: {escalation_type}")
                return
            
            # Create notifications for each channel
            for channel in rule["channels"]:
                notification = NotificationCreate(
                    patient_id=patient_id,
                    channel=channel,
                    template_id=template.id,
                    priority=rule["priority"],
                    status="pending",
                    scheduled_at=datetime.utcnow() + timedelta(hours=rule["delay_hours"]),
                    metadata={
                        "type": escalation_type,
                        "escalation_rule": rule,
                        **metadata
                    }
                )
                
                # Save notification
                self.db.add(Notification(**notification.dict()))
            
            # Notify staff if required
            if rule.get("notify_staff"):
                await self._notify_staff(patient_id, escalation_type, metadata)
            
            # Notify emergency services if required
            if rule.get("notify_emergency"):
                await self._notify_emergency(patient_id, metadata)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error creating escalation notification: {str(e)}")
            raise

    async def _notify_staff(
        self,
        patient_id: str,
        escalation_type: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Notify staff about escalation"""
        try:
            # TODO: Implement staff notification
            # This could involve creating a task, sending an email, or using a staff notification system
            logger.info(f"Notifying staff about {escalation_type} escalation for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error notifying staff: {str(e)}")
            raise

    async def _notify_emergency(
        self,
        patient_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Notify emergency services"""
        try:
            # TODO: Implement emergency services notification
            # This could involve calling emergency services API or sending alerts
            logger.info(f"Notifying emergency services for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error notifying emergency services: {str(e)}")
            raise

    async def handle_escalation_response(
        self,
        notification_id: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle response to escalation notification"""
        try:
            # Get notification
            notification = self.db.query(Notification)\
                .filter(Notification.id == notification_id)\
                .first()
            
            if not notification:
                logger.error(f"Notification not found: {notification_id}")
                return
            
            # Update notification status
            notification.status = "responded"
            notification.response = response
            if metadata:
                notification.metadata.update(metadata)
            
            # Handle response based on escalation type
            escalation_type = notification.metadata.get("type")
            if escalation_type == "missed_appointment":
                await self._handle_missed_appointment_response(notification)
            elif escalation_type == "medication_adherence":
                await self._handle_medication_adherence_response(notification)
            elif escalation_type == "test_results":
                await self._handle_test_results_response(notification)
            elif escalation_type == "emergency":
                await self._handle_emergency_response(notification)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error handling escalation response: {str(e)}")
            raise

    async def _handle_missed_appointment_response(
        self,
        notification: Notification
    ) -> None:
        """Handle response to missed appointment escalation"""
        try:
            # Get appointment
            appointment_id = notification.metadata.get("appointment_id")
            appointment = self.db.query(FollowUpSchedule)\
                .filter(FollowUpSchedule.id == appointment_id)\
                .first()
            
            if not appointment:
                logger.error(f"Appointment not found: {appointment_id}")
                return
            
            # Update appointment status based on response
            response = notification.response.lower()
            if "confirm" in response or "yes" in response:
                appointment.status = ScheduleStatus.CONFIRMED
            elif "reschedule" in response:
                appointment.status = ScheduleStatus.RESCHEDULED
            elif "cancel" in response or "no" in response:
                appointment.status = ScheduleStatus.CANCELLED
        except Exception as e:
            logger.error(f"Error handling missed appointment response: {str(e)}")
            raise

    async def _handle_medication_adherence_response(
        self,
        notification: Notification
    ) -> None:
        """Handle response to medication adherence escalation"""
        try:
            # TODO: Implement medication adherence response handling
            # This would involve updating medication logs and potentially scheduling follow-ups
            pass
        except Exception as e:
            logger.error(f"Error handling medication adherence response: {str(e)}")
            raise

    async def _handle_test_results_response(
        self,
        notification: Notification
    ) -> None:
        """Handle response to test results escalation"""
        try:
            # TODO: Implement test results response handling
            # This would involve updating test result status and potentially scheduling follow-ups
            pass
        except Exception as e:
            logger.error(f"Error handling test results response: {str(e)}")
            raise

    async def _handle_emergency_response(
        self,
        notification: Notification
    ) -> None:
        """Handle response to emergency escalation"""
        try:
            # TODO: Implement emergency response handling
            # This would involve coordinating with emergency services and updating patient status
            pass
        except Exception as e:
            logger.error(f"Error handling emergency response: {str(e)}")
            raise 