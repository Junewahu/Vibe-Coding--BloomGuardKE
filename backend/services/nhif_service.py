import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from ..config import settings
from ..models.nhif import NHIFMember, NHIFClaim, NHIFVerificationLog
from ..schemas.nhif import NHIFVerificationRequest, NHIFVerificationResponse, NHIFClaimResponse

class NHIFService:
    def __init__(self):
        self.api_key = settings.NHIF_API_KEY
        self.api_url = settings.NHIF_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def verify_member(self, request: NHIFVerificationRequest) -> NHIFVerificationResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/verify-member",
                    json={
                        "member_number": request.member_number,
                        "id_number": request.id_number
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    return NHIFVerificationResponse(
                        success=True,
                        member=NHIFMember(
                            member_number=data["member"]["member_number"],
                            first_name=data["member"]["first_name"],
                            last_name=data["member"]["last_name"],
                            id_number=data["member"]["id_number"],
                            phone_number=data["member"]["phone_number"],
                            email=data["member"].get("email"),
                            date_of_birth=datetime.fromisoformat(data["member"]["date_of_birth"]),
                            gender=data["member"]["gender"],
                            employer_name=data["member"].get("employer_name"),
                            employer_code=data["member"].get("employer_code"),
                            membership_type=data["member"]["membership_type"],
                            membership_status=data["member"]["membership_status"],
                            dependents=data["member"].get("dependents", []),
                            last_verification=datetime.utcnow(),
                            verification_status="verified"
                        )
                    )
                else:
                    return NHIFVerificationResponse(
                        success=False,
                        error=data.get("error", "Verification failed")
                    )
        except Exception as e:
            return NHIFVerificationResponse(
                success=False,
                error=str(e)
            )

    async def submit_claim(self, claim: NHIFClaim) -> NHIFClaimResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/claims",
                    json={
                        "member_number": claim.member.member_number,
                        "facility_code": claim.facility.facility_code,
                        "service_date": claim.service_date.isoformat(),
                        "claim_type": claim.claim_type,
                        "diagnosis": claim.diagnosis,
                        "treatment": claim.treatment,
                        "amount_claimed": claim.amount_claimed,
                        "documents": claim.documents
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    return NHIFClaimResponse(
                        success=True,
                        claim=NHIFClaim(
                            **claim.dict(),
                            claim_number=data["claim_number"],
                            status="submitted"
                        )
                    )
                else:
                    return NHIFClaimResponse(
                        success=False,
                        error=data.get("error", "Claim submission failed")
                    )
        except Exception as e:
            return NHIFClaimResponse(
                success=False,
                error=str(e)
            )

    async def check_claim_status(self, claim_number: str) -> NHIFClaimResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/claims/{claim_number}",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    return NHIFClaimResponse(
                        success=True,
                        claim=NHIFClaim(
                            claim_number=claim_number,
                            status=data["status"],
                            amount_approved=data.get("amount_approved"),
                            rejection_reason=data.get("rejection_reason"),
                            payment_date=datetime.fromisoformat(data["payment_date"]) if data.get("payment_date") else None,
                            payment_reference=data.get("payment_reference")
                        )
                    )
                else:
                    return NHIFClaimResponse(
                        success=False,
                        error=data.get("error", "Failed to get claim status")
                    )
        except Exception as e:
            return NHIFClaimResponse(
                success=False,
                error=str(e)
            )

    async def get_member_benefits(self, member_number: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/members/{member_number}/benefits",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

nhif_service = NHIFService() 