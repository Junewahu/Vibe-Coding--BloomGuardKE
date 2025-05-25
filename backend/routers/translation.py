from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from ..database import get_db
from ..services.translation import translation_service
from ..auth import get_current_active_user
from ..models.user import User
from ..models.patient import Patient

router = APIRouter()

@router.get("/languages", response_model=Dict[str, str])
async def get_supported_languages():
    """Get all supported languages."""
    return translation_service.get_supported_languages()

@router.post("/translate")
async def translate_text(
    text: str,
    target_language: str,
    source_language: Optional[str] = None
):
    """Translate text to target language."""
    try:
        translated_text = await translation_service.translate_text(
            text=text,
            target_language=target_language,
            source_language=source_language
        )
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/translate-template")
async def translate_template(
    template_name: str,
    context: Dict[str, str],
    target_language: str
):
    """Translate a template's context to target language."""
    try:
        translated_context = await translation_service.translate_template(
            template_name=template_name,
            context=context,
            target_language=target_language
        )
        return {"translated_context": translated_context}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put("/patient/{patient_id}/language")
async def update_patient_language(
    patient_id: int,
    preferred_language: str,
    secondary_languages: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update patient's language preferences."""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Validate language
        supported_languages = translation_service.get_supported_languages()
        if preferred_language not in supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {preferred_language}"
            )
        
        if secondary_languages:
            for lang in secondary_languages:
                if lang not in supported_languages:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported secondary language: {lang}"
                    )
        
        # Update patient's language preferences
        patient.preferred_language = preferred_language
        if secondary_languages:
            patient.secondary_languages = secondary_languages
        
        db.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/patient/{patient_id}/language")
async def get_patient_language(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient's language preferences."""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        return {
            "preferred_language": patient.preferred_language,
            "secondary_languages": patient.secondary_languages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 