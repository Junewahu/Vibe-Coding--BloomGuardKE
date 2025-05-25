from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from ..models.patient import Patient
from ..models.user import User
from ..schemas.patient import PatientCreate
from ..schemas.user import UserCreate
from .patient import create_patient
from .user import create_user
from ..core.security import get_password_hash

def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate patient data and return list of errors."""
    errors = []
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    
    if data.get('email') and not '@' in data['email']:
        errors.append("Invalid email format")
    
    if data.get('phone_number') and not data['phone_number'].isdigit():
        errors.append("Phone number must contain only digits")
    
    return errors

def process_excel_import(
    db: Session,
    file_path: str,
    created_by_id: int
) -> Dict[str, Any]:
    """Process Excel file for bulk patient import."""
    try:
        df = pd.read_excel(file_path)
        results = {
            'total': len(df),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for index, row in df.iterrows():
            patient_data = row.to_dict()
            errors = validate_patient_data(patient_data)
            
            if errors:
                results['failed'] += 1
                results['errors'].append({
                    'row': index + 2,  # Excel is 1-indexed and has header
                    'errors': errors
                })
                continue
            
            try:
                # Create patient
                patient_in = PatientCreate(
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name'],
                    date_of_birth=patient_data['date_of_birth'],
                    gender=patient_data['gender'],
                    email=patient_data.get('email'),
                    phone_number=patient_data.get('phone_number'),
                    address=patient_data.get('address'),
                    medical_history=patient_data.get('medical_history'),
                    created_by_id=created_by_id
                )
                
                patient = create_patient(db, patient_in)
                results['successful'] += 1
                
                # Create caregiver if specified
                if patient_data.get('caregiver_email'):
                    caregiver_in = UserCreate(
                        email=patient_data['caregiver_email'],
                        password=get_password_hash("changeme"),  # Temporary password
                        first_name=patient_data.get('caregiver_first_name', ''),
                        last_name=patient_data.get('caregiver_last_name', ''),
                        phone_number=patient_data.get('caregiver_phone'),
                        role='caregiver'
                    )
                    caregiver = create_user(db, caregiver_in)
                    patient.caregivers.append(caregiver)
                    db.commit()
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'row': index + 2,
                    'errors': [str(e)]
                })
        
        return results
    
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")

def process_csv_import(
    db: Session,
    file_path: str,
    created_by_id: int
) -> Dict[str, Any]:
    """Process CSV file for bulk patient import."""
    try:
        df = pd.read_csv(file_path)
        return process_excel_import(db, df, created_by_id)
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

def get_import_template() -> bytes:
    """Generate and return an Excel template for patient import."""
    template_data = {
        'first_name': ['John'],
        'last_name': ['Doe'],
        'date_of_birth': ['2000-01-01'],
        'gender': ['M'],
        'email': ['john.doe@example.com'],
        'phone_number': ['254700000000'],
        'address': ['123 Main St'],
        'medical_history': ['None'],
        'caregiver_email': ['caregiver@example.com'],
        'caregiver_first_name': ['Jane'],
        'caregiver_last_name': ['Doe'],
        'caregiver_phone': ['254711111111']
    }
    
    df = pd.DataFrame(template_data)
    return df.to_excel(index=False) 