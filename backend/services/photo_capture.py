from typing import Optional, Dict, Any
import os
from PIL import Image
import qrcode
from io import BytesIO
import base64
from ..config import settings
from ..models.patient import Patient
from sqlalchemy.orm import Session

class PhotoCaptureService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.card_template_path = os.path.join(self.upload_dir, "card_template.png")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "photos"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "cards"), exist_ok=True)
    
    def save_patient_photo(
        self,
        patient_id: int,
        photo_data: bytes,
        db: Session
    ) -> str:
        """Save patient photo and update patient record."""
        try:
            # Process and save photo
            photo_path = os.path.join(self.upload_dir, "photos", f"patient_{patient_id}.jpg")
            
            # Open and process image
            img = Image.open(BytesIO(photo_data))
            
            # Resize to standard dimensions
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            
            # Save processed image
            img.save(photo_path, "JPEG", quality=95)
            
            # Update patient record
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                patient.photo_path = photo_path
                db.commit()
            
            return photo_path
        except Exception as e:
            raise Exception(f"Error saving patient photo: {str(e)}")
    
    def generate_patient_card(
        self,
        patient_id: int,
        db: Session
    ) -> bytes:
        """Generate patient ID card with photo and QR code."""
        try:
            # Get patient data
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                raise Exception("Patient not found")
            
            # Load card template
            template = Image.open(self.card_template_path)
            
            # Add patient photo
            if patient.photo_path and os.path.exists(patient.photo_path):
                photo = Image.open(patient.photo_path)
                template.paste(photo, (50, 50))
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"Patient ID: {patient.id}\nName: {patient.first_name} {patient.last_name}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Add QR code to card
            template.paste(qr_img, (50, 400))
            
            # Save card
            card_path = os.path.join(self.upload_dir, "cards", f"patient_{patient_id}_card.png")
            template.save(card_path)
            
            # Return card as bytes
            with open(card_path, "rb") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error generating patient card: {str(e)}")
    
    def get_patient_photo(
        self,
        patient_id: int,
        db: Session
    ) -> Optional[bytes]:
        """Get patient photo if exists."""
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient or not patient.photo_path:
                return None
            
            if os.path.exists(patient.photo_path):
                with open(patient.photo_path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            raise Exception(f"Error getting patient photo: {str(e)}")

# Create singleton instance
photo_capture_service = PhotoCaptureService() 