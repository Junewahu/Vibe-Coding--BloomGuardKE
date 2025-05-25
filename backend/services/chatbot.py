from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.notification import Notification, NotificationTemplate
from ..models.patient import Patient
from ..models.scheduling import FollowUpSchedule
from ..schemas.notification import NotificationCreate
from ..schemas.scheduling import FollowUpScheduleCreate
import re
import json

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self, db: Session):
        self.db = db
        self.intents = self._load_intents()
        self.context = {}

    def _load_intents(self) -> Dict[str, Any]:
        """Load chatbot intents from configuration"""
        return {
            "greeting": {
                "patterns": [
                    r"hi|hello|hey|greetings",
                    r"good (morning|afternoon|evening)",
                    r"how are you"
                ],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Greetings! How may I assist you?"
                ]
            },
            "appointment": {
                "patterns": [
                    r"schedule|book|make an appointment",
                    r"when is my (next )?appointment",
                    r"reschedule|change appointment",
                    r"cancel appointment"
                ],
                "responses": {
                    "schedule": "I'll help you schedule an appointment. What type of appointment do you need?",
                    "check": "Let me check your upcoming appointments.",
                    "reschedule": "I'll help you reschedule your appointment. Which appointment would you like to change?",
                    "cancel": "I'll help you cancel your appointment. Which appointment would you like to cancel?"
                }
            },
            "medication": {
                "patterns": [
                    r"medication|medicine|prescription",
                    r"when to take|dosage|how many",
                    r"side effects|reactions",
                    r"refill|renew prescription"
                ],
                "responses": {
                    "info": "Let me check your medication information.",
                    "dosage": "Here's your medication schedule:",
                    "side_effects": "Here are the possible side effects:",
                    "refill": "I'll help you request a prescription refill."
                }
            },
            "emergency": {
                "patterns": [
                    r"emergency|urgent|immediate",
                    r"severe pain|bleeding|fever",
                    r"can't breathe|chest pain"
                ],
                "responses": [
                    "This seems urgent. Please call emergency services immediately.",
                    "For emergencies, please call 911 or go to the nearest emergency room.",
                    "This requires immediate medical attention. Please seek emergency care."
                ]
            },
            "general_info": {
                "patterns": [
                    r"clinic hours|opening times",
                    r"location|address|directions",
                    r"contact|phone number|email",
                    r"insurance|coverage|payment"
                ],
                "responses": {
                    "hours": "Our clinic hours are Monday to Friday, 9 AM to 5 PM.",
                    "location": "We are located at 123 Medical Center Drive.",
                    "contact": "You can reach us at (555) 123-4567 or info@clinic.com",
                    "insurance": "We accept most major insurance providers. Would you like to check your coverage?"
                }
            },
            "feedback": {
                "patterns": [
                    r"feedback|review|rating",
                    r"complaint|issue|problem",
                    r"suggestion|improve|better"
                ],
                "responses": [
                    "Thank you for your feedback. We'll use it to improve our services.",
                    "I'm sorry to hear about your experience. Let me help you with that.",
                    "Your feedback is valuable to us. Thank you for sharing."
                ]
            }
        }

    async def process_message(
        self,
        patient_id: str,
        message: str,
        channel: str
    ) -> Dict[str, Any]:
        """Process incoming message and generate response"""
        try:
            # Get patient context
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                return {
                    "response": "I'm sorry, I couldn't find your patient record.",
                    "action": None
                }

            # Detect intent
            intent = self._detect_intent(message)
            if not intent:
                return {
                    "response": "I'm not sure I understand. Could you please rephrase?",
                    "action": None
                }

            # Generate response based on intent
            response = await self._generate_response(intent, message, patient)
            
            # Create notification record
            notification = NotificationCreate(
                patient_id=patient_id,
                channel=channel,
                message=message,
                response=response["response"],
                status="processed",
                metadata={
                    "intent": intent,
                    "action": response.get("action"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Save notification
            self.db.add(Notification(**notification.dict()))
            self.db.commit()
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect intent from message"""
        message = message.lower()
        
        for intent, data in self.intents.items():
            for pattern in data["patterns"]:
                if re.search(pattern, message):
                    return intent
        
        return None

    async def _generate_response(
        self,
        intent: str,
        message: str,
        patient: Patient
    ) -> Dict[str, Any]:
        """Generate response based on intent"""
        try:
            if intent == "greeting":
                return {
                    "response": self._get_random_response(self.intents["greeting"]["responses"]),
                    "action": None
                }
            
            elif intent == "appointment":
                return await self._handle_appointment_intent(message, patient)
            
            elif intent == "medication":
                return await self._handle_medication_intent(message, patient)
            
            elif intent == "emergency":
                return {
                    "response": self._get_random_response(self.intents["emergency"]["responses"]),
                    "action": "emergency_alert"
                }
            
            elif intent == "general_info":
                return await self._handle_general_info_intent(message)
            
            elif intent == "feedback":
                return {
                    "response": self._get_random_response(self.intents["feedback"]["responses"]),
                    "action": "store_feedback"
                }
            
            else:
                return {
                    "response": "I'm not sure how to help with that. Would you like to speak with a staff member?",
                    "action": "transfer_to_staff"
                }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def _handle_appointment_intent(
        self,
        message: str,
        patient: Patient
    ) -> Dict[str, Any]:
        """Handle appointment-related intents"""
        try:
            message = message.lower()
            
            if "schedule" in message or "book" in message:
                return {
                    "response": self.intents["appointment"]["responses"]["schedule"],
                    "action": "schedule_appointment"
                }
            
            elif "when" in message or "next" in message:
                # Get next appointment
                next_appointment = self.db.query(FollowUpSchedule)\
                    .filter(FollowUpSchedule.patient_id == patient.id)\
                    .filter(FollowUpSchedule.status == "pending")\
                    .order_by(FollowUpSchedule.start_date)\
                    .first()
                
                if next_appointment:
                    return {
                        "response": f"Your next appointment is on {next_appointment.start_date.strftime('%B %d, %Y at %I:%M %p')}.",
                        "action": None
                    }
                else:
                    return {
                        "response": "You don't have any upcoming appointments.",
                        "action": None
                    }
            
            elif "reschedule" in message or "change" in message:
                return {
                    "response": self.intents["appointment"]["responses"]["reschedule"],
                    "action": "reschedule_appointment"
                }
            
            elif "cancel" in message:
                return {
                    "response": self.intents["appointment"]["responses"]["cancel"],
                    "action": "cancel_appointment"
                }
            
            else:
                return {
                    "response": "I can help you schedule, check, reschedule, or cancel appointments. What would you like to do?",
                    "action": None
                }
        except Exception as e:
            logger.error(f"Error handling appointment intent: {str(e)}")
            raise

    async def _handle_medication_intent(
        self,
        message: str,
        patient: Patient
    ) -> Dict[str, Any]:
        """Handle medication-related intents"""
        try:
            message = message.lower()
            
            if "when" in message or "dosage" in message:
                return {
                    "response": self.intents["medication"]["responses"]["dosage"],
                    "action": "get_medication_schedule"
                }
            
            elif "side" in message or "effect" in message:
                return {
                    "response": self.intents["medication"]["responses"]["side_effects"],
                    "action": "get_medication_info"
                }
            
            elif "refill" in message or "renew" in message:
                return {
                    "response": self.intents["medication"]["responses"]["refill"],
                    "action": "request_refill"
                }
            
            else:
                return {
                    "response": "I can help you with medication schedules, side effects, or prescription refills. What would you like to know?",
                    "action": None
                }
        except Exception as e:
            logger.error(f"Error handling medication intent: {str(e)}")
            raise

    async def _handle_general_info_intent(
        self,
        message: str
    ) -> Dict[str, Any]:
        """Handle general information intents"""
        try:
            message = message.lower()
            
            if "hour" in message or "time" in message:
                return {
                    "response": self.intents["general_info"]["responses"]["hours"],
                    "action": None
                }
            
            elif "location" in message or "address" in message:
                return {
                    "response": self.intents["general_info"]["responses"]["location"],
                    "action": "send_location"
                }
            
            elif "contact" in message or "phone" in message:
                return {
                    "response": self.intents["general_info"]["responses"]["contact"],
                    "action": None
                }
            
            elif "insurance" in message or "coverage" in message:
                return {
                    "response": self.intents["general_info"]["responses"]["insurance"],
                    "action": "check_insurance"
                }
            
            else:
                return {
                    "response": "I can provide information about our hours, location, contact details, or insurance coverage. What would you like to know?",
                    "action": None
                }
        except Exception as e:
            logger.error(f"Error handling general info intent: {str(e)}")
            raise

    def _get_random_response(self, responses: List[str]) -> str:
        """Get a random response from the list"""
        import random
        return random.choice(responses)

    async def store_feedback(
        self,
        patient_id: str,
        feedback: str,
        rating: Optional[int] = None
    ) -> None:
        """Store patient feedback"""
        try:
            # Create feedback record
            feedback_data = {
                "patient_id": patient_id,
                "feedback": feedback,
                "rating": rating,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # TODO: Implement feedback storage
            logger.info(f"Storing feedback: {json.dumps(feedback_data)}")
        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}")
            raise

    async def transfer_to_staff(
        self,
        patient_id: str,
        reason: str
    ) -> None:
        """Transfer conversation to staff member"""
        try:
            # Create transfer request
            transfer_data = {
                "patient_id": patient_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # TODO: Implement staff transfer logic
            logger.info(f"Transferring to staff: {json.dumps(transfer_data)}")
        except Exception as e:
            logger.error(f"Error transferring to staff: {str(e)}")
            raise 