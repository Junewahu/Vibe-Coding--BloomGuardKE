from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class NHIFMember(Base):
    __tablename__ = "nhif_members"

    id = Column(Integer, primary_key=True, index=True)
    member_number = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    id_number = Column(String, unique=True, index=True)
    phone_number = Column(String)
    email = Column(String, nullable=True)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    employer_name = Column(String, nullable=True)
    employer_code = Column(String, nullable=True)
    membership_type = Column(String)  # e.g., "formal", "informal", "voluntary"
    membership_status = Column(String)  # e.g., "active", "inactive", "suspended"
    dependents = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verification = Column(DateTime, nullable=True)
    verification_status = Column(String, default="pending")

    claims = relationship("NHIFClaim", back_populates="member")

class NHIFClaim(Base):
    __tablename__ = "nhif_claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String, unique=True, index=True)
    member_id = Column(Integer, ForeignKey("nhif_members.id"))
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    service_date = Column(DateTime)
    claim_date = Column(DateTime, default=datetime.utcnow)
    claim_type = Column(String)  # e.g., "inpatient", "outpatient", "dental"
    diagnosis = Column(String)
    treatment = Column(String)
    amount_claimed = Column(Float)
    amount_approved = Column(Float, nullable=True)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    rejection_reason = Column(String, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    payment_reference = Column(String, nullable=True)
    documents = Column(JSON, default=list)  # List of document URLs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status = Column(String, default="pending")  # For offline sync

    member = relationship("NHIFMember", back_populates="claims")
    facility = relationship("Facility", back_populates="claims")

class NHIFVerificationLog(Base):
    __tablename__ = "nhif_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("nhif_members.id"))
    verification_date = Column(DateTime, default=datetime.utcnow)
    verification_type = Column(String)  # e.g., "initial", "renewal", "status_check"
    status = Column(String)
    response_data = Column(JSON)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("NHIFMember") 