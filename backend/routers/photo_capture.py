from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..services.photo_capture import photo_capture_service
from ..auth import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.post("/photo/{patient_id}")
async def capture_patient_photo(
    patient_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Capture and save patient photo."""
    try:
        photo_data = await photo.read()
        photo_path = photo_capture_service.save_patient_photo(
            patient_id=patient_id,
            photo_data=photo_data,
            db=db
        )
        return {"message": "Photo saved successfully", "photo_path": photo_path}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/photo/{patient_id}")
async def get_patient_photo(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient photo."""
    try:
        photo_data = photo_capture_service.get_patient_photo(
            patient_id=patient_id,
            db=db
        )
        if not photo_data:
            raise HTTPException(
                status_code=404,
                detail="Photo not found"
            )
        return Response(
            content=photo_data,
            media_type="image/jpeg"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/card/{patient_id}")
async def generate_patient_card(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate patient ID card."""
    try:
        card_data = photo_capture_service.generate_patient_card(
            patient_id=patient_id,
            db=db
        )
        return Response(
            content=card_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=patient_{patient_id}_card.png"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 