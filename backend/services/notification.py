from typing import Optional, List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from africastalking.SMS import SMS
from jinja2 import Environment, FileSystemLoader
from ..config import settings
from .. import crud
from ..database import SessionLocal
from datetime import datetime, timedelta
import json
import requests
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from ..models.notification import Notification, NotificationChannel, NotificationStatus, NotificationPriority, NotificationTemplate, NotificationPreference, NotificationDelivery, NotificationType, NotificationLog, WhatsAppSession, VoiceCall, USSDMenu, USSDSession
from ..schemas.notification import (
    NotificationCreate, NotificationUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationDeliveryCreate, NotificationDeliveryUpdate,
    WhatsAppSessionCreate, VoiceCallCreate, USSDMenuCreate, USSDSessionCreate
)
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.smtp_client = None
        self.twilio_client = None
        self.africastalking_client = None
        self.template_env = Environment(
            loader=FileSystemLoader("templates/notifications")
        )
        self.sms_provider = settings.SMS_PROVIDER
        self.whatsapp_provider = settings.WHATSAPP_PROVIDER
        self.voice_provider = settings.VOICE_PROVIDER
        self.ussd_provider = settings.USSD_PROVIDER
        self._init_clients()
    
    def _init_clients(self):
        """Initialize notification clients"""
        # Initialize SMTP client
        if settings.SMTP_HOST and settings.SMTP_PORT:
            self.smtp_client = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                self.smtp_client.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                self.smtp_client.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # Initialize Twilio client
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        
        # Initialize Africa's Talking client
        if settings.AFRICASTALKING_API_KEY and settings.AFRICASTALKING_USERNAME:
            self.africastalking_client = SMS(
                settings.AFRICASTALKING_USERNAME,
                settings.AFRICASTALKING_API_KEY
            )
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a notification template"""
        template = self.template_env.get_template(f"{template_name}.html")
        return template.render(**context)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """Send email notification using template"""
        if not self.smtp_client:
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Render HTML content
            html_content = self._render_template(template_name, context)
            msg.attach(MIMEText(html_content, "html"))
            
            # Add plain text version
            plain_text = self._render_template(f"{template_name}_text", context)
            msg.attach(MIMEText(plain_text, "plain"))
            
            self.smtp_client.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_sms(
        self,
        to_number: str,
        template_name: str,
        context: Dict[str, Any],
        provider: str = "twilio"
    ) -> bool:
        """Send SMS notification using template"""
        try:
            # Render SMS message from template
            message = self._render_template(f"{template_name}_sms", context)
            
            if provider == "twilio" and self.twilio_client:
                self.twilio_client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=to_number
                )
                return True
            elif provider == "africastalking" and self.africastalking_client:
                response = self.africastalking_client.send(
                    message,
                    [to_number],
                    settings.AFRICASTALKING_SENDER_ID
                )
                return response.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("status") == "Success"
            return False
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    def send_appointment_reminder(
        self,
        appointment_id: int,
        reminder_id: int,
        db: SessionLocal
    ) -> bool:
        """Send appointment reminder"""
        try:
            # Get appointment and reminder details
            appointment = crud.appointment.get_appointment(db, appointment_id)
            reminder = crud.reminder.get_reminder(db, reminder_id)
            
            if not appointment or not reminder:
                return False
            
            # Get patient and doctor details
            patient = crud.patient.get_patient(db, appointment.patient_id)
            doctor = crud.user.get_user(db, appointment.doctor_id)
            
            if not patient or not doctor:
                return False
            
            # Prepare context for templates
            context = {
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "doctor_name": f"{doctor.first_name} {doctor.last_name}",
                "appointment_date": appointment.scheduled_at.strftime("%Y-%m-%d %H:%M"),
                "reason": appointment.reason,
                "location": appointment.location or "Main Clinic"
            }
            
            # Send notifications
            success = True
            
            # Send to patient
            if patient.email:
                success &= self.send_email(
                    patient.email,
                    "Appointment Reminder",
                    "appointment_reminder",
                    context
                )
            if patient.phone_number:
                success &= self.send_sms(
                    patient.phone_number,
                    "appointment_reminder",
                    context
                )
            
            # Send to caregivers
            for caregiver in patient.caregivers:
                if caregiver.email:
                    success &= self.send_email(
                        caregiver.email,
                        "Appointment Reminder",
                        "appointment_reminder",
                        context
                    )
                if caregiver.phone_number:
                    success &= self.send_sms(
                        caregiver.phone_number,
                        "appointment_reminder",
                        context
                    )
            
            # Update reminder status
            if success:
                crud.reminder.mark_reminder_sent(db, reminder_id)
            else:
                crud.reminder.mark_reminder_failed(
                    db,
                    reminder_id,
                    "Failed to send notification"
                )
            
            return success
        except Exception as e:
            print(f"Error sending appointment reminder: {str(e)}")
            return False
    
    def send_follow_up_reminder(
        self,
        medical_record_id: int,
        reminder_id: int,
        db: SessionLocal
    ) -> bool:
        """Send follow-up reminder"""
        try:
            # Get medical record and reminder details
            record = crud.medical_record.get_medical_record(db, medical_record_id)
            reminder = crud.reminder.get_reminder(db, reminder_id)
            
            if not record or not reminder:
                return False
            
            # Get patient and doctor details
            patient = crud.patient.get_patient(db, record.patient_id)
            doctor = crud.user.get_user(db, record.doctor_id)
            
            if not patient or not doctor:
                return False
            
            # Prepare context for templates
            context = {
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "doctor_name": f"{doctor.first_name} {doctor.last_name}",
                "follow_up_date": record.follow_up_date.strftime("%Y-%m-%d"),
                "diagnosis": record.diagnosis,
                "notes": record.notes
            }
            
            # Send notifications
            success = True
            
            # Send to patient
            if patient.email:
                success &= self.send_email(
                    patient.email,
                    "Follow-up Reminder",
                    "follow_up_reminder",
                    context
                )
            if patient.phone_number:
                success &= self.send_sms(
                    patient.phone_number,
                    "follow_up_reminder",
                    context
                )
            
            # Send to caregivers
            for caregiver in patient.caregivers:
                if caregiver.email:
                    success &= self.send_email(
                        caregiver.email,
                        "Follow-up Reminder",
                        "follow_up_reminder",
                        context
                    )
                if caregiver.phone_number:
                    success &= self.send_sms(
                        caregiver.phone_number,
                        "follow_up_reminder",
                        context
                    )
            
            # Update reminder status
            if success:
                crud.reminder.mark_reminder_sent(db, reminder_id)
            else:
                crud.reminder.mark_reminder_failed(
                    db,
                    reminder_id,
                    "Failed to send notification"
                )
            
            return success
        except Exception as e:
            print(f"Error sending follow-up reminder: {str(e)}")
            return False
    
    def send_welcome_notification(
        self,
        user_id: int,
        db: SessionLocal
    ) -> bool:
        """Send welcome notification to new user"""
        try:
            user = crud.user.get_user(db, user_id)
            if not user:
                return False
            
            context = {
                "user_name": f"{user.first_name} {user.last_name}",
                "role": user.role
            }
            
            success = True
            if user.email:
                success &= self.send_email(
                    user.email,
                    "Welcome to BloomGuard",
                    "welcome",
                    context
                )
            if user.phone_number:
                success &= self.send_sms(
                    user.phone_number,
                    "welcome",
                    context
                )
            
            return success
        except Exception as e:
            print(f"Error sending welcome notification: {str(e)}")
            return False
    
    def send_password_reset(
        self,
        email: str,
        reset_token: str,
        db: SessionLocal
    ) -> bool:
        """Send password reset notification"""
        try:
            context = {
                "reset_link": f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            }
            
            return self.send_email(
                email,
                "Password Reset Request",
                "password_reset",
                context
            )
        except Exception as e:
            print(f"Error sending password reset notification: {str(e)}")
            return False

    def send_billing_notification(
        self,
        patient_email: str,
        patient_phone: str,
        patient_name: str,
        invoice_number: str,
        invoice_date: str,
        due_date: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        payment_link: str,
        phone_number: str,
        insurance_info: Optional[Dict[str, str]] = None
    ) -> None:
        """Send a billing notification to a patient."""
        context = {
            "patient_name": patient_name,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "items": items,
            "total_amount": total_amount,
            "payment_link": payment_link,
            "phone_number": phone_number,
            "insurance_info": insurance_info
        }

        # Send email notification
        self.send_email(
            to_email=patient_email,
            subject=f"Billing Notification - Invoice #{invoice_number}",
            template_name="billing_notification",
            context=context
        )

        # Send SMS notification
        self.send_sms(
            to_phone=patient_phone,
            template_name="billing_notification_sms",
            context=context
        )

    def send_payment_confirmation(
        self,
        patient_email: str,
        patient_phone: str,
        patient_name: str,
        invoice_number: str,
        payment_date: str,
        payment_amount: float,
        payment_method: str,
        transaction_id: str
    ) -> None:
        """Send a payment confirmation notification to a patient."""
        context = {
            "patient_name": patient_name,
            "invoice_number": invoice_number,
            "payment_date": payment_date,
            "payment_amount": payment_amount,
            "payment_method": payment_method,
            "transaction_id": transaction_id
        }

        # Send email notification
        self.send_email(
            to_email=patient_email,
            subject=f"Payment Confirmation - Invoice #{invoice_number}",
            template_name="payment_confirmation",
            context=context
        )

        # Send SMS notification
        self.send_sms(
            to_phone=patient_phone,
            template_name="payment_confirmation_sms",
            context=context
        )

    async def send_notification(
        self,
        db: Session,
        patient_id: int,
        template_name: str,
        channel: NotificationChannel,
        context: Dict[str, Any],
        priority: int = 0
    ) -> Notification:
        """Send a notification through the specified channel."""
        # Get patient contact info
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Create notification record
        notification = Notification(
            patient_id=patient_id,
            channel=channel,
            template_name=template_name,
            context=context,
            priority=priority,
            status=NotificationStatus.PENDING
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        try:
            # Send based on channel
            if channel == NotificationChannel.SMS:
                await self._send_sms(patient.phone_number, template_name, context)
            elif channel == NotificationChannel.WHATSAPP:
                await self._send_whatsapp(patient.phone_number, template_name, context)
            elif channel == NotificationChannel.VOICE:
                await self._send_voice(patient.phone_number, template_name, context)
            elif channel == NotificationChannel.USSD:
                await self._send_ussd(patient.phone_number, template_name, context)

            # Update status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            db.commit()
            raise

        return notification

    async def _send_sms(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send SMS using configured provider."""
        if self.sms_provider == "africas_talking":
            await self._send_sms_africas_talking(phone_number, template_name, context)
        elif self.sms_provider == "twilio":
            await self._send_sms_twilio(phone_number, template_name, context)
        else:
            raise ValueError(f"Unsupported SMS provider: {self.sms_provider}")

    async def _send_whatsapp(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send WhatsApp message using configured provider."""
        if self.whatsapp_provider == "whatsapp_cloud":
            await self._send_whatsapp_cloud(phone_number, template_name, context)
        elif self.whatsapp_provider == "twilio":
            await self._send_whatsapp_twilio(phone_number, template_name, context)
        else:
            raise ValueError(f"Unsupported WhatsApp provider: {self.whatsapp_provider}")

    async def _send_voice(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send voice call using configured provider."""
        if self.voice_provider == "africas_talking":
            await self._send_voice_africas_talking(phone_number, template_name, context)
        elif self.voice_provider == "twilio":
            await self._send_voice_twilio(phone_number, template_name, context)
        else:
            raise ValueError(f"Unsupported voice provider: {self.voice_provider}")

    async def _send_ussd(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send USSD prompt using configured provider."""
        if self.ussd_provider == "africas_talking":
            await self._send_ussd_africas_talking(phone_number, template_name, context)
        else:
            raise ValueError(f"Unsupported USSD provider: {self.ussd_provider}")

    # Provider-specific implementations
    async def _send_sms_africas_talking(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send SMS using Africa's Talking API."""
        # Implementation using Africa's Talking API
        pass

    async def _send_sms_twilio(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send SMS using Twilio API."""
        # Implementation using Twilio API
        pass

    async def _send_whatsapp_cloud(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send WhatsApp message using WhatsApp Cloud API."""
        # Implementation using WhatsApp Cloud API
        pass

    async def _send_whatsapp_twilio(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send WhatsApp message using Twilio API."""
        # Implementation using Twilio API
        pass

    async def _send_voice_africas_talking(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send voice call using Africa's Talking API."""
        # Implementation using Africa's Talking API
        pass

    async def _send_voice_twilio(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send voice call using Twilio API."""
        # Implementation using Twilio API
        pass

    async def _send_ussd_africas_talking(
        self,
        phone_number: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send USSD prompt using Africa's Talking API."""
        # Implementation using Africa's Talking API
        pass

    async def check_sim_status(self, phone_number: str) -> Dict[str, Any]:
        """Check SIM card status using provider API."""
        # Implementation for SIM status check
        pass

    async def get_delivery_status(
        self,
        db: Session,
        notification_id: int
    ) -> Dict[str, Any]:
        """Get delivery status of a notification."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        # Implementation for delivery status check
        pass

    async def create_notification(
        self,
        db: Session,
        notification_data: Dict[str, Any]
    ) -> Notification:
        """Create a new notification."""
        try:
            notification = Notification(**notification_data)
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise

    async def get_notification(
        self,
        db: Session,
        notification_id: int
    ) -> Optional[Notification]:
        """Get a notification by ID."""
        return db.query(Notification).filter(Notification.id == notification_id).first()

    async def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        notification_type: Optional[NotificationType] = None,
        channel: Optional[NotificationChannel] = None,
        status: Optional[NotificationStatus] = None,
        priority: Optional[NotificationPriority] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Notification]:
        """Get notifications for a user with optional filters."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        if channel:
            query = query.filter(Notification.channel == channel)
        if status:
            query = query.filter(Notification.status == status)
        if priority:
            query = query.filter(Notification.priority == priority)
        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)
        
        return query.order_by(Notification.created_at.desc()).all()

    async def update_notification(
        self,
        db: Session,
        notification_id: int,
        notification_data: Dict[str, Any]
    ) -> Optional[Notification]:
        """Update a notification."""
        try:
            notification = await self.get_notification(db, notification_id)
            if notification:
                for key, value in notification_data.items():
                    setattr(notification, key, value)
                db.commit()
                db.refresh(notification)
            return notification
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating notification: {str(e)}")
            raise

    async def create_template(
        self,
        db: Session,
        template_data: Dict[str, Any]
    ) -> NotificationTemplate:
        """Create a new notification template."""
        try:
            template = NotificationTemplate(**template_data)
            db.add(template)
            db.commit()
            db.refresh(template)
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating template: {str(e)}")
            raise

    async def get_template(
        self,
        db: Session,
        template_id: int
    ) -> Optional[NotificationTemplate]:
        """Get a template by ID."""
        return db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()

    async def get_templates(
        self,
        db: Session,
        notification_type: Optional[NotificationType] = None,
        channel: Optional[NotificationChannel] = None
    ) -> List[NotificationTemplate]:
        """Get templates with optional filters."""
        query = db.query(NotificationTemplate)
        
        if notification_type:
            query = query.filter(NotificationTemplate.type == notification_type)
        if channel:
            query = query.filter(NotificationTemplate.channel == channel)
        
        return query.all()

    async def update_template(
        self,
        db: Session,
        template_id: int,
        template_data: Dict[str, Any]
    ) -> Optional[NotificationTemplate]:
        """Update a template."""
        try:
            template = await self.get_template(db, template_id)
            if template:
                for key, value in template_data.items():
                    setattr(template, key, value)
                db.commit()
                db.refresh(template)
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating template: {str(e)}")
            raise

    async def create_preference(
        self,
        db: Session,
        preference_data: Dict[str, Any]
    ) -> NotificationPreference:
        """Create a new notification preference."""
        try:
            preference = NotificationPreference(**preference_data)
            db.add(preference)
            db.commit()
            db.refresh(preference)
            return preference
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating preference: {str(e)}")
            raise

    async def get_user_preferences(
        self,
        db: Session,
        user_id: int
    ) -> List[NotificationPreference]:
        """Get notification preferences for a user."""
        return db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).all()

    async def update_preference(
        self,
        db: Session,
        preference_id: int,
        preference_data: Dict[str, Any]
    ) -> Optional[NotificationPreference]:
        """Update a notification preference."""
        try:
            preference = db.query(NotificationPreference).filter(
                NotificationPreference.id == preference_id
            ).first()
            
            if preference:
                for key, value in preference_data.items():
                    setattr(preference, key, value)
                db.commit()
                db.refresh(preference)
            return preference
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating preference: {str(e)}")
            raise

    async def create_delivery(
        self,
        db: Session,
        delivery_data: Dict[str, Any]
    ) -> NotificationDelivery:
        """Create a new notification delivery record."""
        try:
            delivery = NotificationDelivery(**delivery_data)
            db.add(delivery)
            db.commit()
            db.refresh(delivery)
            return delivery
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating delivery: {str(e)}")
            raise

    async def update_delivery(
        self,
        db: Session,
        delivery_id: int,
        delivery_data: Dict[str, Any]
    ) -> Optional[NotificationDelivery]:
        """Update a notification delivery record."""
        try:
            delivery = db.query(NotificationDelivery).filter(
                NotificationDelivery.id == delivery_id
            ).first()
            if delivery:
                for key, value in delivery_data.items():
                    setattr(delivery, key, value)
                db.commit()
                db.refresh(delivery)
            return delivery
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating delivery: {str(e)}")
            raise

    async def get_pending_deliveries(
        self,
        db: Session,
        limit: int = 100
    ) -> List[NotificationDelivery]:
        """Get pending notification deliveries."""
        return db.query(NotificationDelivery).filter(
            NotificationDelivery.status == NotificationStatus.PENDING,
            NotificationDelivery.next_attempt_at <= datetime.utcnow()
        ).limit(limit).all()

    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get comprehensive notification statistics."""
        try:
            # Get total notifications
            total_notifications = self.db.query(func.count(Notification.id)).scalar()

            # Get notifications by channel
            notifications_by_channel = dict(
                self.db.query(
                    Notification.channel,
                    func.count(Notification.id)
                ).group_by(Notification.channel).all()
            )

            # Get notifications by status
            notifications_by_status = dict(
                self.db.query(
                    Notification.status,
                    func.count(Notification.id)
                ).group_by(Notification.status).all()
            )

            # Calculate average response time
            avg_response_time = self.db.query(
                func.avg(
                    func.extract('epoch', Notification.read_time) -
                    func.extract('epoch', Notification.sent_time)
                )
            ).filter(
                Notification.read_time.isnot(None),
                Notification.sent_time.isnot(None)
            ).scalar()

            # Calculate success rate
            total_sent = self.db.query(func.count(Notification.id)).filter(
                Notification.status.in_([
                    NotificationStatus.DELIVERED,
                    NotificationStatus.READ,
                    NotificationStatus.FAILED
                ])
            ).scalar()

            successful = self.db.query(func.count(Notification.id)).filter(
                Notification.status.in_([
                    NotificationStatus.DELIVERED,
                    NotificationStatus.READ
                ])
            ).scalar()

            success_rate = (successful / total_sent * 100) if total_sent > 0 else 0

            # Get recent notifications
            recent_notifications = self.db.query(Notification).order_by(
                Notification.created_at.desc()
            ).limit(10).all()

            # Get active channels
            active_channels = [
                channel.value for channel in NotificationChannel
                if self.db.query(Notification).filter(
                    Notification.channel == channel
                ).first() is not None
            ]

            # Get popular templates
            popular_templates = self.db.query(
                NotificationTemplate,
                func.count(Notification.id).label('usage_count')
            ).join(
                Notification,
                Notification.template_id == NotificationTemplate.id
            ).group_by(
                NotificationTemplate.id
            ).order_by(
                func.count(Notification.id).desc()
            ).limit(5).all()

            return {
                "total_notifications": total_notifications,
                "notifications_by_channel": notifications_by_channel,
                "notifications_by_status": notifications_by_status,
                "average_response_time": avg_response_time,
                "success_rate": success_rate,
                "recent_notifications": recent_notifications,
                "active_channels": active_channels,
                "popular_templates": [template[0] for template in popular_templates]
            }
        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            raise

    async def create_log(
        self,
        db: Session,
        log_data: Dict[str, Any]
    ) -> NotificationLog:
        """Create a new notification log."""
        try:
            log = NotificationLog(**log_data)
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating log: {str(e)}")
            raise

    async def get_notification_logs(
        self,
        db: Session,
        notification_id: int
    ) -> List[NotificationLog]:
        """Get logs for a notification."""
        return db.query(NotificationLog).filter(
            NotificationLog.notification_id == notification_id
        ).order_by(NotificationLog.created_at.desc()).all()

    # Notification Template methods
    def create_notification_template(
        self,
        template: NotificationTemplateCreate,
        created_by: int
    ) -> NotificationTemplate:
        try:
            db_template = NotificationTemplate(
                **template.dict(),
                created_by=created_by
            )
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification template: {str(e)}")
            raise

    def update_notification_template(
        self,
        template_id: int,
        template_update: dict
    ) -> Optional[NotificationTemplate]:
        try:
            db_template = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.id == template_id
            ).first()
            
            if not db_template:
                return None

            for key, value in template_update.items():
                setattr(db_template, key, value)

            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification template: {str(e)}")
            raise

    def get_notification_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        channel: Optional[NotificationChannel] = None
    ) -> List[NotificationTemplate]:
        query = self.db.query(NotificationTemplate)
        
        if is_active is not None:
            query = query.filter(NotificationTemplate.is_active == is_active)
        if channel:
            query = query.filter(NotificationTemplate.channel == channel)
            
        return query.offset(skip).limit(limit).all()

    # Notification methods
    def create_notification(
        self,
        notification: NotificationCreate
    ) -> Notification:
        try:
            db_notification = Notification(**notification.dict())
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            return db_notification
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise

    def update_notification(
        self,
        notification_id: int,
        notification_update: dict
    ) -> Optional[Notification]:
        try:
            db_notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if not db_notification:
                return None

            for key, value in notification_update.items():
                setattr(db_notification, key, value)

            self.db.commit()
            self.db.refresh(db_notification)
            return db_notification
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification: {str(e)}")
            raise

    def get_notifications(
        self,
        patient_id: Optional[int] = None,
        channel: Optional[NotificationChannel] = None,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        query = self.db.query(Notification)
        
        if patient_id:
            query = query.filter(Notification.patient_id == patient_id)
        if channel:
            query = query.filter(Notification.channel == channel)
        if status:
            query = query.filter(Notification.status == status)
            
        return query.offset(skip).limit(limit).all()

    # WhatsApp Session methods
    def create_whatsapp_session(
        self,
        session: WhatsAppSessionCreate
    ) -> WhatsAppSession:
        try:
            db_session = WhatsAppSession(**session.dict())
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            return db_session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating WhatsApp session: {str(e)}")
            raise

    def update_whatsapp_session(
        self,
        session_id: int,
        session_update: dict
    ) -> Optional[WhatsAppSession]:
        try:
            db_session = self.db.query(WhatsAppSession).filter(
                WhatsAppSession.id == session_id
            ).first()
            
            if not db_session:
                return None

            for key, value in session_update.items():
                setattr(db_session, key, value)

            self.db.commit()
            self.db.refresh(db_session)
            return db_session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating WhatsApp session: {str(e)}")
            raise

    def get_whatsapp_sessions(
        self,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WhatsAppSession]:
        query = self.db.query(WhatsAppSession)
        
        if patient_id:
            query = query.filter(WhatsAppSession.patient_id == patient_id)
        if status:
            query = query.filter(WhatsAppSession.status == status)
            
        return query.offset(skip).limit(limit).all()

    # Voice Call methods
    def create_voice_call(
        self,
        call: VoiceCallCreate
    ) -> VoiceCall:
        try:
            db_call = VoiceCall(**call.dict())
            self.db.add(db_call)
            self.db.commit()
            self.db.refresh(db_call)
            return db_call
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating voice call: {str(e)}")
            raise

    def update_voice_call(
        self,
        call_id: int,
        call_update: dict
    ) -> Optional[VoiceCall]:
        try:
            db_call = self.db.query(VoiceCall).filter(
                VoiceCall.id == call_id
            ).first()
            
            if not db_call:
                return None

            for key, value in call_update.items():
                setattr(db_call, key, value)

            self.db.commit()
            self.db.refresh(db_call)
            return db_call
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating voice call: {str(e)}")
            raise

    def get_voice_calls(
        self,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[VoiceCall]:
        query = self.db.query(VoiceCall)
        
        if patient_id:
            query = query.filter(VoiceCall.patient_id == patient_id)
        if status:
            query = query.filter(VoiceCall.status == status)
            
        return query.offset(skip).limit(limit).all()

    # USSD Menu methods
    def create_ussd_menu(
        self,
        menu: USSDMenuCreate,
        created_by: int
    ) -> USSDMenu:
        try:
            db_menu = USSDMenu(
                **menu.dict(),
                created_by=created_by
            )
            self.db.add(db_menu)
            self.db.commit()
            self.db.refresh(db_menu)
            return db_menu
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating USSD menu: {str(e)}")
            raise

    def update_ussd_menu(
        self,
        menu_id: int,
        menu_update: dict
    ) -> Optional[USSDMenu]:
        try:
            db_menu = self.db.query(USSDMenu).filter(
                USSDMenu.id == menu_id
            ).first()
            
            if not db_menu:
                return None

            for key, value in menu_update.items():
                setattr(db_menu, key, value)

            self.db.commit()
            self.db.refresh(db_menu)
            return db_menu
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating USSD menu: {str(e)}")
            raise

    def get_ussd_menus(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[USSDMenu]:
        query = self.db.query(USSDMenu)
        
        if is_active is not None:
            query = query.filter(USSDMenu.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()

    # USSD Session methods
    def create_ussd_session(
        self,
        session: USSDSessionCreate
    ) -> USSDSession:
        try:
            db_session = USSDSession(**session.dict())
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            return db_session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating USSD session: {str(e)}")
            raise

    def update_ussd_session(
        self,
        session_id: int,
        session_update: dict
    ) -> Optional[USSDSession]:
        try:
            db_session = self.db.query(USSDSession).filter(
                USSDSession.id == session_id
            ).first()
            
            if not db_session:
                return None

            for key, value in session_update.items():
                setattr(db_session, key, value)

            self.db.commit()
            self.db.refresh(db_session)
            return db_session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating USSD session: {str(e)}")
            raise

    def get_ussd_sessions(
        self,
        patient_id: Optional[int] = None,
        menu_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[USSDSession]:
        query = self.db.query(USSDSession)
        
        if patient_id:
            query = query.filter(USSDSession.patient_id == patient_id)
        if menu_id:
            query = query.filter(USSDSession.menu_id == menu_id)
            
        return query.offset(skip).limit(limit).all()

# Create singleton instance
notification_service = NotificationService() 