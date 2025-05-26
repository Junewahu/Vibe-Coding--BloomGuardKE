import asyncio
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.communication import Message, MessageStatus
from ..crud import communication as crud
from .communication import communication_service

class SyncService:
    def __init__(self):
        self.is_running = False
        self.sync_interval = 60  # seconds

    async def start(self):
        self.is_running = True
        while self.is_running:
            try:
                await self.sync_pending_messages()
            except Exception as e:
                print(f"Error in sync service: {str(e)}")
            await asyncio.sleep(self.sync_interval)

    async def stop(self):
        self.is_running = False

    async def sync_pending_messages(self):
        db = SessionLocal()
        try:
            # Get pending messages
            pending_messages = crud.get_pending_messages(db)
            
            for message in pending_messages:
                try:
                    # Attempt to send message
                    result = await communication_service.send_message(message)
                    
                    if result["success"]:
                        # Update message status
                        crud.mark_message_sent(db, message.id)
                        
                        # If we have a message ID from the provider, store it
                        if "message_id" in result:
                            crud.update_message(
                                db,
                                message.id,
                                {"provider_message_id": result["message_id"]}
                            )
                    else:
                        # Mark as failed if we get an error
                        crud.mark_message_failed(
                            db,
                            message.id,
                            result.get("error", "Unknown error")
                        )
                except Exception as e:
                    # Log error and continue with next message
                    print(f"Error syncing message {message.id}: {str(e)}")
                    continue
        finally:
            db.close()

    async def sync_message_status(self):
        db = SessionLocal()
        try:
            # Get messages that are sent but not delivered
            sent_messages = crud.get_messages(
                db,
                status=MessageStatus.SENT,
                sync_status="pending"
            )
            
            for message in sent_messages:
                try:
                    # Check message status with provider
                    if message.template.type == "whatsapp":
                        status = await communication_service.check_whatsapp_status(
                            message.provider_message_id
                        )
                    elif message.template.type == "sms":
                        status = await communication_service.check_sms_status(
                            message.provider_message_id
                        )
                    else:
                        continue

                    # Update message status if delivered
                    if status.get("status") == "delivered":
                        crud.mark_message_delivered(db, message.id)
                except Exception as e:
                    print(f"Error checking message status {message.id}: {str(e)}")
                    continue
        finally:
            db.close()

sync_service = SyncService() 