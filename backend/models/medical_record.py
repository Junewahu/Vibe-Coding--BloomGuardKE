from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import BaseModel
from ..database import Base

class RecordType(enum.Enum):
    VACCINATION = "vaccination"
    CHECKUP = "checkup"
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    OTHER = "other"

class MedicalRecord(Base, BaseModel):
    """Medical record model for storing patient medical history"""
    
    # Basic Information
    patient_id = Column(ForeignKey("patient.id"), nullable=False)
    doctor_id = Column(ForeignKey("user.id"), nullable=False)
    record_type = Column(Enum(RecordType), nullable=False)
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    diagnosis = Column(String(500))
    treatment = Column(String(500))
    notes = Column(String(1000))
    
    # Additional Data
    attachments = Column(JSON)  # URLs to attached files
    metadata = Column(JSON)  # Additional structured data
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("User")
    
    def __repr__(self):
        return f"<MedicalRecord {self.id} - {self.record_type.value}>"
    
    @property
    def is_follow_up_due(self):
        if not self.follow_up_required or not self.follow_up_date:
            return False
        return datetime.utcnow() >= self.follow_up_date
    
    def to_dict(self):
        data = super().to_dict()
        data["record_type"] = self.record_type.value
        return data 