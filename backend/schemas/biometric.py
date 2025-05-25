from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BiometricRecordBase(BaseModel):
    patient_id: int
    nhif_id: Optional[str] = None
    biometric_type: str
    provider: str

class BiometricRecordCreate(BiometricRecordBase):
    biometric_data: bytes

class BiometricRecordResponse(BiometricRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 