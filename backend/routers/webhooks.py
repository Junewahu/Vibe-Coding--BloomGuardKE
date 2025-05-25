from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db
from ..providers.whatsapp import WhatsAppProvider
from ..providers.ivr import IVRProvider
from ..providers.ussd import USSDProvider
from ..services.notification import NotificationService
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

# Initialize providers
whatsapp_provider = WhatsAppProvider()
ivr_provider = IVRProvider()
ussd_provider = USSDProvider()

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle incoming WhatsApp webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process webhook
        webhook_data = await whatsapp_provider.handle_webhook(payload)
        
        # Update notification status
        notification_service = NotificationService(db)
        await notification_service.update_notification_status(
            webhook_data["message_id"],
            webhook_data["status"]
        )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ivr/status")
async def ivr_status_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle IVR status webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process webhook
        webhook_data = await ivr_provider.handle_webhook(payload)
        
        # Update call status
        notification_service = NotificationService(db)
        await notification_service.update_voice_call_status(
            webhook_data["call_id"],
            webhook_data["status"],
            {
                "duration": webhook_data["duration"],
                "direction": webhook_data["direction"]
            }
        )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling IVR status webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ivr/menu")
async def ivr_menu_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle IVR menu selection webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process webhook
        webhook_data = await ivr_provider.handle_webhook(payload)
        
        # Get call details
        notification_service = NotificationService(db)
        call = await notification_service.get_voice_call(webhook_data["call_id"])
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Handle menu selection
        response = await ivr_provider.handle_menu_selection(
            webhook_data["call_id"],
            webhook_data["digits"],
            call.menu_options
        )
        
        return response
    except Exception as e:
        logger.error(f"Error handling IVR menu webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ussd")
async def ussd_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle USSD webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process webhook
        webhook_data = await ussd_provider.handle_webhook(payload)
        
        # Handle USSD request
        response = await ussd_provider.handle_request(
            webhook_data["session_id"],
            webhook_data["service_code"],
            webhook_data["text"],
            webhook_data["phone_number"]
        )
        
        return {
            "sessionId": webhook_data["session_id"],
            "message": response,
            "endSession": False
        }
    except Exception as e:
        logger.error(f"Error handling USSD webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ussd/end")
async def ussd_end_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle USSD session end webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process webhook
        webhook_data = await ussd_provider.handle_webhook(payload)
        
        # Update session status
        notification_service = NotificationService(db)
        await notification_service.update_ussd_session_status(
            webhook_data["session_id"],
            "completed"
        )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling USSD end webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 