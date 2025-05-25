from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json
import re
import logging
from ..models.response import (
    Response, ResponseType, ResponseStatus, ResponseEscalation,
    PatientResponse, ResponseFollowUp, ResponseTemplate,
    ResponseAnalytics, ResponseChannel
)
from ..models.notification import Notification
from ..models.patient import Patient
from ..models.user import User
from ..services.notification import notification_service
from ..services.translation import translation_service

logger = logging.getLogger(__name__)

class ResponseService:
    def __init__(self):
        self.faq_patterns = {
            "appointment": r"(?i)(appointment|schedule|booking)",
            "location": r"(?i)(where|location|address|directions)",
            "cost": r"(?i)(cost|price|payment|insurance)",
            "cancellation": r"(?i)(cancel|reschedule|change)",
            "emergency": r"(?i)(emergency|urgent|immediate)"
        }
        self.templates: Dict[str, ResponseTemplate] = {}

    async def process_response(
        self,
        db: Session,
        notification_id: int,
        patient_id: int,
        message: str,
        language: str = "en"
    ) -> Response:
        """Process a patient's response to a notification."""
        # Create response record
        response = Response(
            notification_id=notification_id,
            patient_id=patient_id,
            message=message,
            language=language
        )

        # Determine response type
        response.response_type = self._determine_response_type(message)
        
        # Process based on type
        if response.response_type == ResponseType.QUESTION:
            # Handle with chatbot
            answer = await self._handle_chatbot_query(message, language)
            if answer:
                response.metadata = {"chatbot_response": answer}
                response.status = ResponseStatus.PROCESSED
            else:
                # Escalate if chatbot can't handle
                await self._escalate_response(db, response, "Unhandled question")
        else:
            # Handle other response types
            response.status = ResponseStatus.PROCESSED

        db.add(response)
        db.commit()
        db.refresh(response)

        # Send acknowledgment if needed
        if response.status == ResponseStatus.PROCESSED:
            await self._send_acknowledgment(db, response)

        return response

    def _determine_response_type(self, message: str) -> ResponseType:
        """Determine the type of response based on message content."""
        message = message.lower()
        
        if any(word in message for word in ["yes", "confirm", "ok", "sure"]):
            return ResponseType.CONFIRM
        elif any(word in message for word in ["no", "cancel", "stop"]):
            return ResponseType.CANCEL
        elif any(word in message for word in ["reschedule", "change", "different time"]):
            return ResponseType.RESCHEDULE
        elif "?" in message:
            return ResponseType.QUESTION
        else:
            return ResponseType.FEEDBACK

    async def _handle_chatbot_query(
        self,
        message: str,
        language: str
    ) -> Optional[str]:
        """Handle a question using the chatbot."""
        # Translate to English if needed
        if language != "en":
            message = await translation_service.translate_text(message, language, "en")

        # Identify question category
        category = None
        for cat, pattern in self.faq_patterns.items():
            if re.search(pattern, message):
                category = cat
                break

        if not category:
            return None

        # Get answer from FAQ database
        answer = await self._get_faq_answer(category, message)
        
        # Translate answer back if needed
        if language != "en" and answer:
            answer = await translation_service.translate_text(answer, "en", language)

        return answer

    async def _get_faq_answer(self, category: str, question: str) -> Optional[str]:
        """Get answer from FAQ database."""
        # Implementation would connect to FAQ database or knowledge base
        # For now, return simple responses
        answers = {
            "appointment": "You can schedule an appointment by calling our office or using our online booking system.",
            "location": "We are located at 123 Medical Center Drive. You can find directions on our website.",
            "cost": "Costs vary depending on your insurance coverage. Please contact our billing department for details.",
            "cancellation": "You can cancel or reschedule your appointment by calling our office at least 24 hours in advance.",
            "emergency": "For emergencies, please call 911 or go to the nearest emergency room."
        }
        return answers.get(category)

    async def _escalate_response(
        self,
        db: Session,
        response: Response,
        reason: str
    ) -> None:
        """Escalate a response to staff."""
        # Find available staff member
        staff = db.query(User).filter(
            and_(
                User.is_active == True,
                User.role.in_(["doctor", "nurse", "receptionist"])
            )
        ).first()

        if staff:
            escalation = ResponseEscalation(
                response_id=response.id,
                escalated_to_id=staff.id,
                reason=reason
            )
            db.add(escalation)
            response.status = ResponseStatus.ESCALATED
            db.commit()

            # Notify staff
            await notification_service.send_notification(
                db=db,
                patient_id=staff.id,
                template_name="response_escalation",
                channel="whatsapp",
                context={
                    "response_id": response.id,
                    "patient_name": response.patient.full_name,
                    "message": response.message,
                    "reason": reason
                }
            )

    async def _send_acknowledgment(
        self,
        db: Session,
        response: Response
    ) -> None:
        """Send acknowledgment to patient."""
        context = {
            "patient_name": response.patient.full_name,
            "response_type": response.response_type.value
        }

        if response.response_type == ResponseType.QUESTION and response.metadata:
            context["answer"] = response.metadata.get("chatbot_response")

        await notification_service.send_notification(
            db=db,
            patient_id=response.patient_id,
            template_name="response_acknowledgment",
            channel=response.notification.channel,
            context=context,
            language=response.language
        )

    async def get_patient_responses(
        self,
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Response]:
        """Get all responses for a patient."""
        return db.query(Response)\
            .filter(Response.patient_id == patient_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    async def get_escalated_responses(
        self,
        db: Session,
        staff_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Response]:
        """Get all escalated responses assigned to a staff member."""
        return db.query(Response)\
            .join(ResponseEscalation)\
            .filter(
                and_(
                    ResponseEscalation.escalated_to_id == staff_id,
                    Response.status == ResponseStatus.ESCALATED
                )
            )\
            .offset(skip)\
            .limit(limit)\
            .all()

    async def resolve_response(
        self,
        db: Session,
        response_id: int,
        resolution_notes: str
    ) -> Response:
        """Mark a response as resolved."""
        response = db.query(Response).filter(Response.id == response_id).first()
        if not response:
            raise ValueError(f"Response {response_id} not found")

        response.status = ResponseStatus.RESOLVED
        response.resolved_at = datetime.utcnow()
        
        if response.escalation:
            response.escalation.resolved_at = datetime.utcnow()
            response.escalation.notes = resolution_notes

        db.commit()
        db.refresh(response)
        return response

    async def create_patient_response(self, db: Session, response_data: Dict[str, Any]) -> PatientResponse:
        """Create a new patient response."""
        response = PatientResponse(**response_data)
        db.add(response)
        db.commit()
        db.refresh(response)
        return response

    async def get_patient_response(self, db: Session, response_id: int) -> Optional[PatientResponse]:
        """Get a patient response by ID."""
        return db.query(PatientResponse).filter(PatientResponse.id == response_id).first()

    async def update_patient_response(
        self,
        db: Session,
        response_id: int,
        response_data: Dict[str, Any]
    ) -> Optional[PatientResponse]:
        """Update a patient response."""
        response = await self.get_patient_response(db, response_id)
        if not response:
            return None

        for key, value in response_data.items():
            setattr(response, key, value)

        db.commit()
        db.refresh(response)
        return response

    async def get_patient_responses(
        self,
        db: Session,
        reminder_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        response_type: Optional[ResponseType] = None,
        channel: Optional[ResponseChannel] = None,
        status: Optional[ResponseStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PatientResponse]:
        """Get patient responses with filters."""
        query = db.query(PatientResponse)

        if reminder_id:
            query = query.filter(PatientResponse.reminder_id == reminder_id)
        if patient_id:
            query = query.filter(PatientResponse.patient_id == patient_id)
        if response_type:
            query = query.filter(PatientResponse.response_type == response_type)
        if channel:
            query = query.filter(PatientResponse.response_channel == channel)
        if status:
            query = query.filter(PatientResponse.status == status)
        if start_date:
            query = query.filter(PatientResponse.response_time >= start_date)
        if end_date:
            query = query.filter(PatientResponse.response_time <= end_date)

        return query.all()

    async def create_follow_up(
        self,
        db: Session,
        follow_up_data: Dict[str, Any]
    ) -> ResponseFollowUp:
        """Create a new follow-up action."""
        follow_up = ResponseFollowUp(**follow_up_data)
        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)
        return follow_up

    async def get_follow_up(self, db: Session, follow_up_id: int) -> Optional[ResponseFollowUp]:
        """Get a follow-up action by ID."""
        return db.query(ResponseFollowUp).filter(ResponseFollowUp.id == follow_up_id).first()

    async def update_follow_up(
        self,
        db: Session,
        follow_up_id: int,
        follow_up_data: Dict[str, Any]
    ) -> Optional[ResponseFollowUp]:
        """Update a follow-up action."""
        follow_up = await self.get_follow_up(db, follow_up_id)
        if not follow_up:
            return None

        for key, value in follow_up_data.items():
            setattr(follow_up, key, value)

        db.commit()
        db.refresh(follow_up)
        return follow_up

    async def get_pending_follow_ups(
        self,
        db: Session,
        response_id: Optional[int] = None
    ) -> List[ResponseFollowUp]:
        """Get pending follow-up actions."""
        query = db.query(ResponseFollowUp).filter(ResponseFollowUp.status == "pending")
        if response_id:
            query = query.filter(ResponseFollowUp.response_id == response_id)
        return query.all()

    async def create_template(self, db: Session, template_data: Dict[str, Any]) -> ResponseTemplate:
        """Create a new response template."""
        template = ResponseTemplate(**template_data)
        db.add(template)
        db.commit()
        db.refresh(template)
        self.templates[f"{template.response_type}_{template.channel}"] = template
        return template

    async def get_template(self, db: Session, template_id: int) -> Optional[ResponseTemplate]:
        """Get a template by ID."""
        return db.query(ResponseTemplate).filter(ResponseTemplate.id == template_id).first()

    async def update_template(
        self,
        db: Session,
        template_id: int,
        template_data: Dict[str, Any]
    ) -> Optional[ResponseTemplate]:
        """Update a template."""
        template = await self.get_template(db, template_id)
        if not template:
            return None

        for key, value in template_data.items():
            setattr(template, key, value)

        db.commit()
        db.refresh(template)
        self.templates[f"{template.response_type}_{template.channel}"] = template
        return template

    async def process_response(
        self,
        db: Session,
        response_id: int
    ) -> Tuple[PatientResponse, List[ResponseFollowUp]]:
        """Process a patient response and create necessary follow-up actions."""
        response = await self.get_patient_response(db, response_id)
        if not response:
            raise ValueError("Response not found")

        # Update response status
        response.status = ResponseStatus.PROCESSING
        response.processed_time = datetime.utcnow()
        db.commit()

        follow_ups = []
        try:
            # Create follow-up actions based on response type
            if response.response_type == ResponseType.RESCHEDULE:
                follow_up = await self.create_follow_up(
                    db,
                    {
                        "response_id": response.id,
                        "action_type": "reschedule",
                        "status": "pending",
                        "action_data": response.response_data,
                        "scheduled_time": datetime.utcnow()
                    }
                )
                follow_ups.append(follow_up)

            elif response.response_type == ResponseType.CANCEL:
                follow_up = await self.create_follow_up(
                    db,
                    {
                        "response_id": response.id,
                        "action_type": "notify_staff",
                        "status": "pending",
                        "action_data": {
                            "reason": "appointment_cancelled",
                            "response_data": response.response_data
                        },
                        "scheduled_time": datetime.utcnow()
                    }
                )
                follow_ups.append(follow_up)

            # Update response status
            response.status = ResponseStatus.COMPLETED
            db.commit()

        except Exception as e:
            logger.error(f"Error processing response {response_id}: {str(e)}")
            response.status = ResponseStatus.FAILED
            response.error_message = str(e)
            db.commit()

        return response, follow_ups

    async def update_analytics(
        self,
        db: Session,
        response: PatientResponse
    ) -> ResponseAnalytics:
        """Update response analytics."""
        today = datetime.utcnow().date()
        analytics = db.query(ResponseAnalytics).filter(
            and_(
                func.date(ResponseAnalytics.date) == today,
                ResponseAnalytics.response_type == response.response_type,
                ResponseAnalytics.channel == response.response_channel
            )
        ).first()

        if not analytics:
            analytics = ResponseAnalytics(
                date=datetime.utcnow(),
                response_type=response.response_type,
                channel=response.response_channel,
                count=0,
                success_rate=0.0,
                average_response_time=0.0
            )
            db.add(analytics)

        # Update analytics
        analytics.count += 1

        # Calculate success rate
        total_responses = db.query(PatientResponse).filter(
            and_(
                func.date(PatientResponse.response_time) == today,
                PatientResponse.response_type == response.response_type,
                PatientResponse.response_channel == response.response_channel
            )
        ).count()
        successful_responses = db.query(PatientResponse).filter(
            and_(
                func.date(PatientResponse.response_time) == today,
                PatientResponse.response_type == response.response_type,
                PatientResponse.response_channel == response.response_channel,
                PatientResponse.status == ResponseStatus.COMPLETED
            )
        ).count()
        analytics.success_rate = (successful_responses / total_responses * 100) if total_responses > 0 else 0

        # Calculate average response time
        response_times = []
        responses = db.query(PatientResponse).filter(
            and_(
                func.date(PatientResponse.response_time) == today,
                PatientResponse.response_type == response.response_type,
                PatientResponse.response_channel == response.response_channel,
                PatientResponse.status == ResponseStatus.COMPLETED
            )
        ).all()
        for r in responses:
            if r.processed_time:
                response_time = (r.processed_time - r.response_time).total_seconds()
                response_times.append(response_time)
        analytics.average_response_time = sum(response_times) / len(response_times) if response_times else 0

        db.commit()
        db.refresh(analytics)
        return analytics

    async def get_response_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive response statistics."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Get responses
        responses = await self.get_patient_responses(
            db,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate statistics
        total_responses = len(responses)
        successful_responses = len([r for r in responses if r.status == ResponseStatus.COMPLETED])
        response_rate = (successful_responses / total_responses * 100) if total_responses > 0 else 0

        # Calculate average response time
        response_times = []
        for response in responses:
            if response.processed_time:
                response_time = (response.processed_time - response.response_time).total_seconds()
                response_times.append(response_time)
        average_response_time = sum(response_times) / len(response_times) if response_times else None

        # Get response type distribution
        response_type_distribution = {}
        for response in responses:
            response_type = response.response_type.value
            response_type_distribution[response_type] = response_type_distribution.get(response_type, 0) + 1

        # Get channel distribution
        channel_distribution = {}
        for response in responses:
            channel = response.response_channel.value
            channel_distribution[channel] = channel_distribution.get(channel, 0) + 1

        # Get recent responses and pending follow-ups
        recent_responses = sorted(
            responses,
            key=lambda x: x.response_time,
            reverse=True
        )[:5]

        pending_follow_ups = await self.get_pending_follow_ups(db)

        return {
            "total_responses": total_responses,
            "response_rate": response_rate,
            "average_response_time": average_response_time,
            "response_type_distribution": response_type_distribution,
            "channel_distribution": channel_distribution,
            "success_rate": response_rate,
            "recent_responses": recent_responses,
            "pending_follow_ups": pending_follow_ups
        }

# Create singleton instance
response_service = ResponseService() 