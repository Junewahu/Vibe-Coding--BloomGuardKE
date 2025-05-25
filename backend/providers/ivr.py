from typing import Dict, Any, Optional, List
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from ..config import settings
import logging
from ..models.notification import VoiceCall
from ..schemas.notification import VoiceCallCreate

logger = logging.getLogger(__name__)

class IVRProvider:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    async def initiate_call(
        self,
        to_number: str,
        call_data: VoiceCallCreate,
        menu_options: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Initiate an IVR call"""
        try:
            # Generate TwiML for the call
            twiml = self._generate_twiml(call_data.message, menu_options)
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                twiml=twiml,
                status_callback=f"{settings.API_BASE_URL}/webhooks/ivr/status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            return {
                "call_id": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction
            }
        except Exception as e:
            logger.error(f"Error initiating IVR call: {str(e)}")
            raise

    def _generate_twiml(
        self,
        message: str,
        menu_options: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate TwiML for the IVR call"""
        response = VoiceResponse()
        
        # Add initial message
        response.say(message, voice="Polly.Joanna")
        
        if menu_options:
            # Create menu with options
            gather = Gather(
                input='dtmf',
                timeout=10,
                num_digits=1,
                action=f"{settings.API_BASE_URL}/webhooks/ivr/menu"
            )
            
            # Add menu instructions
            gather.say("Please select an option:", voice="Polly.Joanna")
            
            # Add menu options
            for option in menu_options:
                gather.say(f"Press {option['digit']} for {option['description']}", voice="Polly.Joanna")
            
            response.append(gather)
            
            # Add fallback for no input
            response.say("No input received. Goodbye.", voice="Polly.Joanna")
        
        return str(response)

    async def handle_menu_selection(
        self,
        call_sid: str,
        digits: str,
        menu_options: List[Dict[str, Any]]
    ) -> str:
        """Handle menu selection and generate appropriate response"""
        try:
            response = VoiceResponse()
            
            # Find selected option
            selected_option = next(
                (option for option in menu_options if option['digit'] == digits),
                None
            )
            
            if selected_option:
                # Handle the selected option
                if 'action' in selected_option:
                    # Execute custom action
                    action_response = await self._execute_menu_action(
                        selected_option['action'],
                        call_sid
                    )
                    response.say(action_response, voice="Polly.Joanna")
                else:
                    # Play default response
                    response.say(
                        selected_option.get('response', 'Thank you for your selection.'),
                        voice="Polly.Joanna"
                    )
            else:
                # Invalid selection
                response.say("Invalid selection. Please try again.", voice="Polly.Joanna")
                response.redirect(f"{settings.API_BASE_URL}/webhooks/ivr/menu")
            
            return str(response)
        except Exception as e:
            logger.error(f"Error handling menu selection: {str(e)}")
            raise

    async def _execute_menu_action(
        self,
        action: str,
        call_sid: str
    ) -> str:
        """Execute custom menu action"""
        try:
            # Map of available actions
            actions = {
                'confirm_appointment': self._handle_appointment_confirmation,
                'reschedule_appointment': self._handle_appointment_rescheduling,
                'speak_to_agent': self._handle_agent_transfer,
                'leave_voicemail': self._handle_voicemail
            }
            
            # Execute the action if available
            if action in actions:
                return await actions[action](call_sid)
            else:
                return "Invalid action selected."
        except Exception as e:
            logger.error(f"Error executing menu action: {str(e)}")
            raise

    async def _handle_appointment_confirmation(self, call_sid: str) -> str:
        """Handle appointment confirmation"""
        # TODO: Implement appointment confirmation logic
        return "Your appointment has been confirmed. Thank you."

    async def _handle_appointment_rescheduling(self, call_sid: str) -> str:
        """Handle appointment rescheduling"""
        # TODO: Implement appointment rescheduling logic
        return "Please call our office during business hours to reschedule your appointment."

    async def _handle_agent_transfer(self, call_sid: str) -> str:
        """Handle transfer to agent"""
        # TODO: Implement agent transfer logic
        return "Please hold while we transfer you to an agent."

    async def _handle_voicemail(self, call_sid: str) -> str:
        """Handle voicemail recording"""
        # TODO: Implement voicemail recording logic
        return "Please leave your message after the tone."

    async def update_call_status(
        self,
        call: VoiceCall,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VoiceCall:
        """Update call status"""
        try:
            call.status = status
            if metadata:
                call.metadata = metadata
            return call
        except Exception as e:
            logger.error(f"Error updating call status: {str(e)}")
            raise

    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming webhook from Twilio"""
        try:
            return {
                "call_id": payload.get("CallSid"),
                "status": payload.get("CallStatus"),
                "duration": payload.get("CallDuration"),
                "direction": payload.get("Direction"),
                "digits": payload.get("Digits"),
                "recording_url": payload.get("RecordingUrl"),
                "recording_duration": payload.get("RecordingDuration")
            }
        except Exception as e:
            logger.error(f"Error handling IVR webhook: {str(e)}")
            raise 