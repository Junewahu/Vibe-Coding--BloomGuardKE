from typing import Optional, Dict, Any
import requests
from ..config import settings
from ..models.patient import Patient
from ..models.biometric import BiometricRecord
from sqlalchemy.orm import Session

class BiometricService:
    def __init__(self):
        self.nhif_api_key = settings.NHIF_API_KEY
        self.nhif_api_url = settings.NHIF_API_URL
        self.biometric_provider = settings.BIOMETRIC_PROVIDER
    
    def verify_nhif_id(self, nhif_id: str) -> Dict[str, Any]:
        """Verify NHIF ID with the NHIF API."""
        try:
            response = requests.get(
                f"{self.nhif_api_url}/verify/{nhif_id}",
                headers={"Authorization": f"Bearer {self.nhif_api_key}"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error verifying NHIF ID: {str(e)}")
    
    def capture_fingerprint(
        self,
        patient_id: int,
        fingerprint_data: bytes,
        db: Session
    ) -> BiometricRecord:
        """Capture and store fingerprint data."""
        try:
            # Store fingerprint data
            biometric_record = BiometricRecord(
                patient_id=patient_id,
                biometric_type="fingerprint",
                biometric_data=fingerprint_data,
                provider=self.biometric_provider
            )
            db.add(biometric_record)
            db.commit()
            db.refresh(biometric_record)
            return biometric_record
        except Exception as e:
            db.rollback()
            raise Exception(f"Error capturing fingerprint: {str(e)}")
    
    def capture_facial_id(
        self,
        patient_id: int,
        facial_data: bytes,
        db: Session
    ) -> BiometricRecord:
        """Capture and store facial recognition data."""
        try:
            # Store facial recognition data
            biometric_record = BiometricRecord(
                patient_id=patient_id,
                biometric_type="facial",
                biometric_data=facial_data,
                provider=self.biometric_provider
            )
            db.add(biometric_record)
            db.commit()
            db.refresh(biometric_record)
            return biometric_record
        except Exception as e:
            db.rollback()
            raise Exception(f"Error capturing facial ID: {str(e)}")
    
    def verify_biometric(
        self,
        patient_id: int,
        biometric_type: str,
        biometric_data: bytes,
        db: Session
    ) -> bool:
        """Verify biometric data against stored records."""
        try:
            # Get stored biometric record
            stored_record = db.query(BiometricRecord).filter(
                BiometricRecord.patient_id == patient_id,
                BiometricRecord.biometric_type == biometric_type
            ).first()
            
            if not stored_record:
                return False
            
            # Compare biometric data
            # Note: In a real implementation, this would use proper biometric matching algorithms
            return stored_record.biometric_data == biometric_data
        except Exception as e:
            raise Exception(f"Error verifying biometric: {str(e)}")
    
    def link_nhif_biometric(
        self,
        patient_id: int,
        nhif_id: str,
        biometric_data: bytes,
        biometric_type: str,
        db: Session
    ) -> BiometricRecord:
        """Link NHIF ID with biometric data."""
        try:
            # Verify NHIF ID
            nhif_data = self.verify_nhif_id(nhif_id)
            
            # Store biometric record with NHIF ID
            biometric_record = BiometricRecord(
                patient_id=patient_id,
                nhif_id=nhif_id,
                biometric_type=biometric_type,
                biometric_data=biometric_data,
                provider=self.biometric_provider
            )
            db.add(biometric_record)
            db.commit()
            db.refresh(biometric_record)
            return biometric_record
        except Exception as e:
            db.rollback()
            raise Exception(f"Error linking NHIF biometric: {str(e)}")

# Create singleton instance
biometric_service = BiometricService() 