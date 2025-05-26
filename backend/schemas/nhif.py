from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class DependentBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    relationship: str

class DependentCreate(DependentBase):
    pass

class Dependent(DependentBase):
    id: int
    member_id: int

    class Config:
        orm_mode = True

class NHIFMemberBase(BaseModel):
    member_number: str
    first_name: str
    last_name: str
    id_number: str
    phone_number: str
    email: Optional[str] = None
    date_of_birth: datetime
    gender: str
    employer_name: Optional[str] = None
    employer_code: Optional[str] = None
    membership_type: str
    dependents: List[DependentCreate] = Field(default_factory=list)

class NHIFMemberCreate(NHIFMemberBase):
    pass

class NHIFMemberUpdate(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    employer_name: Optional[str] = None
    employer_code: Optional[str] = None
    membership_type: Optional[str] = None
    dependents: Optional[List[DependentCreate]] = None

class NHIFMember(NHIFMemberBase):
    id: int
    membership_status: str
    last_verification: Optional[datetime]
    verification_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NHIFClaimBase(BaseModel):
    member_id: int
    facility_id: int
    service_date: datetime
    claim_type: str
    diagnosis: str
    treatment: str
    amount_claimed: float
    documents: List[str] = Field(default_factory=list)

class NHIFClaimCreate(NHIFClaimBase):
    pass

class NHIFClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    amount_approved: Optional[float] = None
    rejection_reason: Optional[str] = None
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    sync_status: Optional[str] = None

class NHIFClaim(NHIFClaimBase):
    id: int
    claim_number: str
    claim_date: datetime
    status: ClaimStatus
    amount_approved: Optional[float]
    rejection_reason: Optional[str]
    payment_date: Optional[datetime]
    payment_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    sync_status: str

    class Config:
        orm_mode = True

class NHIFVerificationRequest(BaseModel):
    member_number: str
    id_number: str

class NHIFVerificationResponse(BaseModel):
    success: bool
    member: Optional[NHIFMember] = None
    error: Optional[str] = None

class NHIFClaimResponse(BaseModel):
    success: bool
    claim: Optional[NHIFClaim] = None
    error: Optional[str] = None 