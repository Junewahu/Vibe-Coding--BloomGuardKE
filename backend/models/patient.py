from sqlalchemy import Column, String, Date, Boolean, ForeignKey, JSON, DateTime, Integer, Text, Enum, LargeBinary
from sqlalchemy.orm import relationship
from datetime import date, datetime
import enum
from .base import BaseModel
from ..database import Base

class DigitalConsent(Base):
    __tablename__ = "digital_consents"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    consent_text = Column(Text, nullable=False)
    consent_given = Column(Boolean, default=False)
    consented_at = Column(DateTime, default=datetime.utcnow)
    consented_by = Column(String(100))  # Name or user ID
    method = Column(String(50))  # e.g., digital, paper, verbal
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    patient = relationship("Patient", back_populates="digital_consent")

class PatientAuditLog(Base):
    __tablename__ = "patient_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    action = Column(String(50))  # create, update, delete
    performed_by = Column(String(100))  # user ID or name
    timestamp = Column(DateTime, default=datetime.utcnow)
    changes = Column(JSON)  # Dict of changed fields
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    # Relationships
    patient = relationship("Patient", back_populates="audit_logs")

class BiometricType(str, enum.Enum):
    FINGERPRINT = "fingerprint"
    FACIAL = "facial"
    IRIS = "iris"
    VOICE = "voice"

class BiometricData(Base):
    """Model for storing patient biometric data"""
    __tablename__ = "biometric_data"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    biometric_type = Column(Enum(BiometricType), nullable=False)
    data = Column(LargeBinary)  # Encrypted biometric data
    nhif_id = Column(String)  # NHIF ID if linked
    capture_date = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="biometric_data")

class PatientPhoto(Base):
    """Model for storing patient photos"""
    __tablename__ = "patient_photos"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    photo_data = Column(LargeBinary)  # Encrypted photo data
    photo_type = Column(String)  # profile, id_card, etc.
    capture_date = Column(DateTime, default=datetime.utcnow)
    is_approved = Column(Boolean, default=False)
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="photos")

class BulkImport(Base):
    """Model for tracking bulk patient imports"""
    __tablename__ = "bulk_imports"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_type = Column(String)  # excel, csv, etc.
    total_records = Column(Integer)
    processed_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    status = Column(String)  # pending, processing, completed, failed
    error_log = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="bulk_imports")

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class PatientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    TRANSFERRED = "transferred"

class Patient(Base, BaseModel):
    """Patient model for storing patient information"""
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender))
    
    # Contact Information
    phone_number = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    
    # Medical Information
    nhif_number = Column(String(50))
    blood_type = Column(String(5))
    allergies = Column(JSON)
    chronic_conditions = Column(JSON)
    
    # Additional Information
    biometric_id = Column(String(100))  # For fingerprint/facial recognition
    photo_url = Column(String(200))  # URL to patient photo
    notes = Column(String(500))
    
    # Add photo path field
    photo_path = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_visit_date = Column(Date)
    
    # Record flagging fields
    is_incomplete = Column(Boolean, default=False)
    is_outdated = Column(Boolean, default=False)
    last_verified_at = Column(DateTime)
    
    # Digital consent
    consent_id = Column(Integer, ForeignKey("digital_consents.id"), nullable=True)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    caregivers = relationship("Caregiver", secondary="patient_caregiver", back_populates="patients")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    biometric_records = relationship("BiometricRecord", back_populates="patient")
    follow_ups = relationship("FollowUpSchedule", back_populates="patient")
    notifications = relationship("Notification", back_populates="patient")
    responses = relationship("Response", back_populates="patient")
    
    # Language preferences
    preferred_language = Column(String(10), default="en")  # ISO 639-1 language code
    secondary_languages = Column(JSON)  # List of additional languages
    
    digital_consent = relationship("DigitalConsent", back_populates="patient", uselist=False, foreign_keys=[consent_id])
    audit_logs = relationship("PatientAuditLog", back_populates="patient")
    biometric_data = relationship("BiometricData", back_populates="patient")
    photos = relationship("PatientPhoto", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        ) 

# Add relationships to Patient model
from .user import User
User.bulk_imports = relationship("BulkImport", back_populates="creator")

class Caregiver(Base):
    __tablename__ = "caregivers"

    id = Column(String(36), primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    relationship = Column(String(50))
    phone_number = Column(String(20))
    alternative_phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(200))
    county = Column(String(100))
    sub_county = Column(String(100))
    
    # System Fields
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    patients = relationship("Patient", back_populates="primary_caregiver")
    notifications = relationship("Notification", back_populates="caregiver")
    
    def __repr__(self):
        return f"<Caregiver {self.first_name} {self.last_name}>"

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(String(36), primary_key=True, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"))
    record_type = Column(String(50))
    record_date = Column(DateTime)
    diagnosis = Column(String(500), nullable=True)
    treatment = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)
    attachments = Column(JSON, nullable=True)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    
    def __repr__(self):
        return f"<MedicalRecord {self.record_type} for Patient {self.patient_id}>"

class Immunization(Base):
    __tablename__ = "immunizations"

    id = Column(String(36), primary_key=True, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"))
    vaccine_name = Column(String(100))
    scheduled_date = Column(DateTime)
    administered_date = Column(DateTime, nullable=True)
    batch_number = Column(String(50), nullable=True)
    administered_by = Column(String(100), nullable=True)
    status = Column(String(20))
    certificate_url = Column(String(200), nullable=True)
    
    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="immunizations")
    
    def __repr__(self):
        return f"<Immunization {self.vaccine_name} for Patient {self.patient_id}>" 