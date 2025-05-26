from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..auth import get_current_user
from ..schemas.nhif import (
    NHIFMember,
    NHIFMemberCreate,
    NHIFMemberUpdate,
    NHIFClaim,
    NHIFClaimCreate,
    NHIFClaimUpdate,
    NHIFVerificationRequest,
    NHIFVerificationResponse,
    NHIFClaimResponse
)
from ..crud import nhif as crud
from ..services.nhif_service import nhif_service
from ..models.user import User

router = APIRouter(prefix="/nhif", tags=["nhif"])

@router.post("/verify", response_model=NHIFVerificationResponse)
async def verify_member(
    request: NHIFVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if member already exists
    existing_member = crud.get_member_by_number(db, request.member_number)
    if existing_member:
        return NHIFVerificationResponse(
            success=True,
            member=existing_member
        )

    # Verify with NHIF API
    response = await nhif_service.verify_member(request)
    if response.success and response.member:
        # Create member record
        db_member = crud.create_member(db, response.member)
        
        # Log verification
        crud.create_verification_log(
            db,
            db_member.id,
            "initial",
            "success",
            response.member.dict()
        )
        
        return NHIFVerificationResponse(
            success=True,
            member=db_member
        )
    return response

@router.get("/members", response_model=List[NHIFMember])
async def get_members(
    membership_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    members = crud.get_members(
        db,
        skip=skip,
        limit=limit,
        membership_status=membership_status
    )
    return members

@router.get("/members/{member_id}", response_model=NHIFMember)
async def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = crud.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@router.put("/members/{member_id}", response_model=NHIFMember)
async def update_member(
    member_id: int,
    member: NHIFMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_member = crud.update_member(db, member_id, member)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@router.post("/claims", response_model=NHIFClaimResponse)
async def create_claim(
    claim: NHIFClaimCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create claim record
    db_claim = crud.create_claim(db, claim)
    
    # Submit claim in background
    async def submit_claim_task():
        response = await nhif_service.submit_claim(db_claim)
        if response.success:
            crud.mark_claim_submitted(db, db_claim.id)
        else:
            crud.mark_claim_rejected(
                db,
                db_claim.id,
                response.error or "Claim submission failed"
            )
    
    background_tasks.add_task(submit_claim_task)
    
    return NHIFClaimResponse(
        success=True,
        claim=db_claim
    )

@router.get("/claims", response_model=List[NHIFClaim])
async def get_claims(
    member_id: Optional[int] = None,
    status: Optional[str] = None,
    sync_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    claims = crud.get_claims(
        db,
        skip=skip,
        limit=limit,
        member_id=member_id,
        status=status,
        sync_status=sync_status
    )
    return claims

@router.get("/claims/{claim_id}", response_model=NHIFClaim)
async def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    claim = crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@router.get("/claims/{claim_number}/status", response_model=NHIFClaimResponse)
async def check_claim_status(
    claim_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check claim status with NHIF API
    response = await nhif_service.check_claim_status(claim_number)
    if response.success and response.claim:
        # Update claim record
        db_claim = crud.get_claim_by_number(db, claim_number)
        if db_claim:
            if response.claim.status == "approved":
                crud.mark_claim_approved(
                    db,
                    db_claim.id,
                    response.claim.amount_approved,
                    response.claim.payment_reference
                )
            elif response.claim.status == "rejected":
                crud.mark_claim_rejected(
                    db,
                    db_claim.id,
                    response.claim.rejection_reason
                )
    return response

@router.get("/members/{member_number}/benefits")
async def get_member_benefits(
    member_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify member exists
    member = crud.get_member_by_number(db, member_number)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Get benefits from NHIF API
    benefits = await nhif_service.get_member_benefits(member_number)
    return benefits 