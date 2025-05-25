from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any
import tempfile
import os

from ..database import get_db
from ..crud import patient_import
from ..auth import get_current_active_user, check_admin_permission
from ..models.user import User

router = APIRouter()

@router.post("/import/excel", response_model=Dict[str, Any])
async def import_patients_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import patients from Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        results = patient_import.process_excel_import(
            db=db,
            file_path=temp_file_path,
            created_by_id=current_user.id
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/import/csv", response_model=Dict[str, Any])
async def import_patients_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import patients from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        results = patient_import.process_csv_import(
            db=db,
            file_path=temp_file_path,
            created_by_id=current_user.id
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/import/template")
async def get_import_template(
    current_user: User = Depends(get_current_active_user)
):
    """Get Excel template for patient import."""
    try:
        template_bytes = patient_import.get_import_template()
        return Response(
            content=template_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=patient_import_template.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 