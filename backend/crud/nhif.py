from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.nhif import NHIFMember, NHIFClaim, NHIFVerificationLog
from ..schemas.nhif import NHIFMemberCreate, NHIFMemberUpdate, NHIFClaimCreate, NHIFClaimUpdate

def get_member(db: Session, member_id: int) -> Optional[NHIFMember]:
    return db.query(NHIFMember).filter(NHIFMember.id == member_id).first()

def get_member_by_number(db: Session, member_number: str) -> Optional[NHIFMember]:
    return db.query(NHIFMember).filter(NHIFMember.member_number == member_number).first()

def get_members(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    membership_status: Optional[str] = None
) -> List[NHIFMember]:
    query = db.query(NHIFMember)
    if membership_status:
        query = query.filter(NHIFMember.membership_status == membership_status)
    return query.offset(skip).limit(limit).all()

def create_member(db: Session, member: NHIFMemberCreate) -> NHIFMember:
    db_member = NHIFMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def update_member(
    db: Session,
    member_id: int,
    member: NHIFMemberUpdate
) -> Optional[NHIFMember]:
    db_member = get_member(db, member_id)
    if db_member:
        update_data = member.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_member, field, value)
        db.commit()
        db.refresh(db_member)
    return db_member

def create_verification_log(
    db: Session,
    member_id: int,
    verification_type: str,
    status: str,
    response_data: dict,
    error_message: Optional[str] = None
) -> NHIFVerificationLog:
    log = NHIFVerificationLog(
        member_id=member_id,
        verification_type=verification_type,
        status=status,
        response_data=response_data,
        error_message=error_message
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_claim(db: Session, claim_id: int) -> Optional[NHIFClaim]:
    return db.query(NHIFClaim).filter(NHIFClaim.id == claim_id).first()

def get_claim_by_number(db: Session, claim_number: str) -> Optional[NHIFClaim]:
    return db.query(NHIFClaim).filter(NHIFClaim.claim_number == claim_number).first()

def get_claims(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    member_id: Optional[int] = None,
    status: Optional[str] = None,
    sync_status: Optional[str] = None
) -> List[NHIFClaim]:
    query = db.query(NHIFClaim)
    if member_id:
        query = query.filter(NHIFClaim.member_id == member_id)
    if status:
        query = query.filter(NHIFClaim.status == status)
    if sync_status:
        query = query.filter(NHIFClaim.sync_status == sync_status)
    return query.offset(skip).limit(limit).all()

def create_claim(db: Session, claim: NHIFClaimCreate) -> NHIFClaim:
    db_claim = NHIFClaim(**claim.dict())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

def update_claim(
    db: Session,
    claim_id: int,
    claim: NHIFClaimUpdate
) -> Optional[NHIFClaim]:
    db_claim = get_claim(db, claim_id)
    if db_claim:
        update_data = claim.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_claim, field, value)
        db.commit()
        db.refresh(db_claim)
    return db_claim

def get_pending_claims(db: Session, limit: int = 100) -> List[NHIFClaim]:
    return db.query(NHIFClaim).filter(
        NHIFClaim.status == "pending",
        NHIFClaim.sync_status == "pending"
    ).limit(limit).all()

def mark_claim_submitted(db: Session, claim_id: int) -> Optional[NHIFClaim]:
    db_claim = get_claim(db, claim_id)
    if db_claim:
        db_claim.status = "submitted"
        db_claim.sync_status = "synced"
        db.commit()
        db.refresh(db_claim)
    return db_claim

def mark_claim_approved(
    db: Session,
    claim_id: int,
    amount_approved: float,
    payment_reference: str
) -> Optional[NHIFClaim]:
    db_claim = get_claim(db, claim_id)
    if db_claim:
        db_claim.status = "approved"
        db_claim.amount_approved = amount_approved
        db_claim.payment_reference = payment_reference
        db_claim.payment_date = datetime.utcnow()
        db_claim.sync_status = "synced"
        db.commit()
        db.refresh(db_claim)
    return db_claim

def mark_claim_rejected(
    db: Session,
    claim_id: int,
    rejection_reason: str
) -> Optional[NHIFClaim]:
    db_claim = get_claim(db, claim_id)
    if db_claim:
        db_claim.status = "rejected"
        db_claim.rejection_reason = rejection_reason
        db_claim.sync_status = "synced"
        db.commit()
        db.refresh(db_claim)
    return db_claim 