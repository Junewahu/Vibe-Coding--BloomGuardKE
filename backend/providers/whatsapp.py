from typing import Dict, Any, Optional
import requests
from twilio.rest import Client
from ..config import settings
import logging
from ..models.notification import WhatsAppSession
from ..schemas.notification import WhatsAppSessionCreate

logger = logging.getLogger(__name__)

class WhatsAppProvider:
    def __init__(self):
        self.provider = settings.WHATSAPP_PROVIDER
        self._init_clients()

    def _init_clients(self):
        """Initialize WhatsApp clients based on provider"""
        if self.provider == "whatsapp_cloud":
            self.client = {
                "access_token": settings.WHATSAPP_ACCESS_TOKEN,
                "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
                "business_account_id": settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
                "api_version": settings.WHATSAPP_API_VERSION
            }
        elif self.provider == "twilio":
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        else:
            raise ValueError(f"Unsupported WhatsApp provider: {self.provider}")

    async def send_message(
        self,
        to_number: str,
        message: str,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None,
        session: Optional[WhatsAppSession] = None
    ) -> Dict[str, Any]:
        """Send a WhatsApp message"""
        try:
            if self.provider == "whatsapp_cloud":
                return await self._send_whatsapp_cloud(
                    to_number,
                    message,
                    template_name,
                    template_params
                )
            elif self.provider == "twilio":
                return await self._send_twilio(
                    to_number,
                    message,
                    template_name,
                    template_params
                )
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise

    async def _send_whatsapp_cloud(
        self,
        to_number: str,
        message: str,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send message using WhatsApp Cloud API"""
        url = f"https://graph.facebook.com/v{self.client['api_version']}/{self.client['phone_number_id']}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.client['access_token']}",
            "Content-Type": "application/json"
        }

        if template_name:
            # Send template message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": value}
                                for value in template_params.values()
                            ]
                        }
                    ]
                }
            }
        else:
            # Send text message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    async def _send_twilio(
        self,
        to_number: str,
        message: str,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send message using Twilio API"""
        if template_name:
            # Format message with template parameters
            message = message.format(**template_params)

        message = self.client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            body=message,
            to=f"whatsapp:{to_number}"
        )
        return {"message_id": message.sid}

    async def create_session(
        self,
        session_data: WhatsAppSessionCreate
    ) -> WhatsAppSession:
        """Create a new WhatsApp session"""
        try:
            if self.provider == "whatsapp_cloud":
                # Initialize session with WhatsApp Cloud API
                url = f"https://graph.facebook.com/v{self.client['api_version']}/{self.client['business_account_id']}/phone_numbers"
                headers = {
                    "Authorization": f"Bearer {self.client['access_token']}",
                    "Content-Type": "application/json"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                # Create session with verified phone number
                return WhatsAppSession(**session_data.dict())
            else:
                # For Twilio, just create the session
                return WhatsAppSession(**session_data.dict())
        except Exception as e:
            logger.error(f"Error creating WhatsApp session: {str(e)}")
            raise

    async def update_session(
        self,
        session: WhatsAppSession,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WhatsAppSession:
        """Update WhatsApp session status"""
        try:
            session.status = status
            if metadata:
                session.metadata = metadata
            return session
        except Exception as e:
            logger.error(f"Error updating WhatsApp session: {str(e)}")
            raise

    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming webhook from WhatsApp"""
        try:
            if self.provider == "whatsapp_cloud":
                return await self._handle_whatsapp_cloud_webhook(payload)
            elif self.provider == "twilio":
                return await self._handle_twilio_webhook(payload)
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {str(e)}")
            raise

    async def _handle_whatsapp_cloud_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle WhatsApp Cloud API webhook"""
        try:
            # Extract message details
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [{}])[0]

            return {
                "message_id": messages.get("id"),
                "from": messages.get("from"),
                "timestamp": messages.get("timestamp"),
                "type": messages.get("type"),
                "text": messages.get("text", {}).get("body"),
                "status": "received"
            }
        except Exception as e:
            logger.error(f"Error handling WhatsApp Cloud webhook: {str(e)}")
            raise

    async def _handle_twilio_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Twilio webhook"""
        try:
            return {
                "message_id": payload.get("MessageSid"),
                "from": payload.get("From").replace("whatsapp:", ""),
                "timestamp": payload.get("MessageTimestamp"),
                "type": "text",
                "text": payload.get("Body"),
                "status": "received"
            }
        except Exception as e:
            logger.error(f"Error handling Twilio webhook: {str(e)}")
            raise 