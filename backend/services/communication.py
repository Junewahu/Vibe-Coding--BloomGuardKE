from typing import Optional, Dict, Any
import httpx
from ..config import settings
from ..models.communication import MessageType, Message
from ..crud.communication import mark_message_sent, mark_message_delivered, mark_message_failed

class CommunicationService:
    def __init__(self):
        self.whatsapp_api_key = settings.WHATSAPP_API_KEY
        self.sms_api_key = settings.SMS_API_KEY
        self.voice_api_key = settings.VOICE_API_KEY
        self.whatsapp_api_url = settings.WHATSAPP_API_URL
        self.sms_api_url = settings.SMS_API_URL
        self.voice_api_url = settings.VOICE_API_URL

    async def send_whatsapp_message(self, message: Message) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.whatsapp_api_url}/messages",
                    json={
                        "to": message.recipient,
                        "template": {
                            "name": message.template.name,
                            "language": message.template.language,
                            "components": [
                                {
                                    "type": "body",
                                    "parameters": [
                                        {"type": "text", "text": value}
                                        for value in message.variables.values()
                                    ]
                                }
                            ]
                        }
                    },
                    headers={"Authorization": f"Bearer {self.whatsapp_api_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to send WhatsApp message: {str(e)}")

    async def send_sms_message(self, message: Message) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sms_api_url}/messages",
                    json={
                        "to": message.recipient,
                        "message": self._format_message_content(message),
                    },
                    headers={"Authorization": f"Bearer {self.sms_api_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to send SMS message: {str(e)}")

    async def send_voice_message(self, message: Message) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.voice_api_url}/calls",
                    json={
                        "to": message.recipient,
                        "message": self._format_message_content(message),
                    },
                    headers={"Authorization": f"Bearer {self.voice_api_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to send voice message: {str(e)}")

    def _format_message_content(self, message: Message) -> str:
        content = message.template.content
        for key, value in message.variables.items():
            content = content.replace(f"{{{key}}}", value)
        return content

    async def send_message(self, message: Message) -> Dict[str, Any]:
        try:
            if message.template.type == MessageType.WHATSAPP:
                result = await self.send_whatsapp_message(message)
            elif message.template.type == MessageType.SMS:
                result = await self.send_sms_message(message)
            elif message.template.type == MessageType.VOICE:
                result = await self.send_voice_message(message)
            else:
                raise ValueError(f"Unsupported message type: {message.template.type}")

            return {
                "success": True,
                "message_id": result.get("message_id"),
                "status": result.get("status")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

communication_service = CommunicationService() 