from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class BiometricRecord(Base):
    __tablename__ = "biometric_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    nhif_id = Column(String, unique=True, index=True, nullable=True)
    biometric_type = Column(String)  # fingerprint, facial, etc.
    biometric_data = Column(LargeBinary)
    provider = Column(String)  # NHIF, custom, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="biometric_records") 