from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import pandas as pd
import io
from ..models.patient import (
    Patient, BiometricData, PatientPhoto, BulkImport,
    BiometricType, Caregiver, MedicalRecord, Immunization, PatientStatus
)
from ..schemas.patient import (
    BiometricDataCreate, BiometricDataUpdate,
    PatientPhotoCreate, PatientPhotoUpdate,
    BulkImportCreate, BulkImportUpdate,
    ImportStats,
    PatientCreate, PatientUpdate,
    CaregiverCreate, CaregiverUpdate,
    MedicalRecordCreate, MedicalRecordUpdate,
    ImmunizationCreate, ImmunizationUpdate
)
import uuid
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, db: Session):
        self.db = db

    # Biometric Data Management
    async def create_biometric_data(
        self,
        patient_id: int,
        biometric_data: BiometricDataCreate
    ) -> BiometricData:
        """Create new biometric data for a patient."""
        try:
            biometric = BiometricData(
                patient_id=patient_id,
                **biometric_data.dict()
            )
            self.db.add(biometric)
            self.db.commit()
            self.db.refresh(biometric)
            return biometric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating biometric data: {str(e)}")
            raise

    async def update_biometric_data(
        self,
        biometric_id: int,
        biometric_data: BiometricDataUpdate
    ) -> BiometricData:
        """Update biometric data."""
        try:
            biometric = self.db.query(BiometricData).filter(
                BiometricData.id == biometric_id
            ).first()
            if not biometric:
                raise ValueError("Biometric data not found")

            for key, value in biometric_data.dict(exclude_unset=True).items():
                setattr(biometric, key, value)

            self.db.commit()
            self.db.refresh(biometric)
            return biometric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating biometric data: {str(e)}")
            raise

    async def get_biometric_data(
        self,
        patient_id: int,
        biometric_type: Optional[BiometricType] = None
    ) -> List[BiometricData]:
        """Get biometric data for a patient."""
        try:
            query = self.db.query(BiometricData).filter(
                BiometricData.patient_id == patient_id
            )

            if biometric_type:
                query = query.filter(BiometricData.biometric_type == biometric_type)

            return query.order_by(desc(BiometricData.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting biometric data: {str(e)}")
            raise

    # Patient Photo Management
    async def create_patient_photo(
        self,
        patient_id: int,
        photo_data: PatientPhotoCreate
    ) -> PatientPhoto:
        """Create new photo for a patient."""
        try:
            photo = PatientPhoto(
                patient_id=patient_id,
                **photo_data.dict()
            )
            self.db.add(photo)
            self.db.commit()
            self.db.refresh(photo)
            return photo
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating patient photo: {str(e)}")
            raise

    async def update_patient_photo(
        self,
        photo_id: int,
        photo_data: PatientPhotoUpdate
    ) -> PatientPhoto:
        """Update patient photo."""
        try:
            photo = self.db.query(PatientPhoto).filter(
                PatientPhoto.id == photo_id
            ).first()
            if not photo:
                raise ValueError("Photo not found")

            for key, value in photo_data.dict(exclude_unset=True).items():
                setattr(photo, key, value)

            self.db.commit()
            self.db.refresh(photo)
            return photo
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating patient photo: {str(e)}")
            raise

    async def get_patient_photos(
        self,
        patient_id: int,
        photo_type: Optional[str] = None
    ) -> List[PatientPhoto]:
        """Get photos for a patient."""
        try:
            query = self.db.query(PatientPhoto).filter(
                PatientPhoto.patient_id == patient_id
            )

            if photo_type:
                query = query.filter(PatientPhoto.photo_type == photo_type)

            return query.order_by(desc(PatientPhoto.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting patient photos: {str(e)}")
            raise

    # Bulk Import Management
    async def create_bulk_import(
        self,
        import_data: BulkImportCreate,
        user_id: int
    ) -> BulkImport:
        """Create new bulk import record."""
        try:
            bulk_import = BulkImport(
                **import_data.dict(),
                created_by=user_id,
                status="pending"
            )
            self.db.add(bulk_import)
            self.db.commit()
            self.db.refresh(bulk_import)
            return bulk_import
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating bulk import: {str(e)}")
            raise

    async def process_bulk_import(
        self,
        import_id: int,
        file_data: bytes
    ) -> BulkImport:
        """Process bulk import file."""
        try:
            bulk_import = self.db.query(BulkImport).filter(
                BulkImport.id == import_id
            ).first()
            if not bulk_import:
                raise ValueError("Bulk import not found")

            # Update status to processing
            bulk_import.status = "processing"
            self.db.commit()

            # Process file based on type
            if bulk_import.file_type == "excel":
                df = pd.read_excel(io.BytesIO(file_data))
            elif bulk_import.file_type == "csv":
                df = pd.read_csv(io.BytesIO(file_data))
            else:
                raise ValueError(f"Unsupported file type: {bulk_import.file_type}")

            # Process records
            total_records = len(df)
            successful_records = 0
            failed_records = 0
            error_log = []

            for _, row in df.iterrows():
                try:
                    # Create patient record
                    patient_data = row.to_dict()
                    patient = Patient(**patient_data)
                    self.db.add(patient)
                    successful_records += 1
                except Exception as e:
                    failed_records += 1
                    error_log.append(f"Error processing record: {str(e)}")

            # Update import record
            bulk_import.total_records = total_records
            bulk_import.processed_records = total_records
            bulk_import.successful_records = successful_records
            bulk_import.failed_records = failed_records
            bulk_import.status = "completed" if failed_records == 0 else "completed_with_errors"
            bulk_import.error_log = "\n".join(error_log) if error_log else None

            self.db.commit()
            self.db.refresh(bulk_import)
            return bulk_import
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing bulk import: {str(e)}")
            raise

    async def get_import_stats(self) -> ImportStats:
        """Get bulk import statistics."""
        try:
            imports = self.db.query(BulkImport).all()
            
            total_imports = len(imports)
            successful_imports = len([i for i in imports if i.status == "completed"])
            failed_imports = len([i for i in imports if i.status == "failed"])
            
            # Calculate success rate
            total_records = sum(i.total_records for i in imports)
            successful_records = sum(i.successful_records for i in imports)
            average_success_rate = (
                successful_records / total_records if total_records > 0 else 0
            )

            # Count imports by type
            imports_by_type = {}
            for import_record in imports:
                file_type = import_record.file_type
                imports_by_type[file_type] = imports_by_type.get(file_type, 0) + 1

            # Get recent imports
            recent_imports = sorted(
                imports,
                key=lambda x: x.created_at,
                reverse=True
            )[:10]

            return ImportStats(
                total_imports=total_imports,
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                average_success_rate=average_success_rate,
                imports_by_type=imports_by_type,
                recent_imports=recent_imports
            )
        except Exception as e:
            logger.error(f"Error getting import stats: {str(e)}")
            raise

    # Patient Registration and Profiling
    async def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient record"""
        try:
            # Create caregiver if provided
            primary_caregiver = None
            if patient_data.primary_caregiver:
                primary_caregiver = Caregiver(
                    id=str(uuid.uuid4()),
                    **patient_data.primary_caregiver.dict()
                )
                self.db.add(primary_caregiver)
                self.db.flush()

            # Create patient
            patient = Patient(
                id=str(uuid.uuid4()),
                primary_caregiver_id=primary_caregiver.id if primary_caregiver else None,
                **patient_data.dict(exclude={'primary_caregiver'})
            )
            
            # Check if record is complete
            patient.is_complete = self._check_record_completeness(patient)
            
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            
            return patient
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            raise

    async def update_patient(
        self,
        patient_id: str,
        patient_data: PatientUpdate
    ) -> Optional[Patient]:
        """Update an existing patient record"""
        try:
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                return None

            # Update patient fields
            for field, value in patient_data.dict(exclude_unset=True).items():
                setattr(patient, field, value)

            # Update completeness check
            patient.is_complete = self._check_record_completeness(patient)
            patient.last_updated = datetime.utcnow()

            self.db.commit()
            self.db.refresh(patient)
            
            return patient
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating patient: {str(e)}")
            raise

    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        try:
            return self.db.query(Patient).filter(Patient.id == patient_id).first()
        except Exception as e:
            logger.error(f"Error getting patient: {str(e)}")
            raise

    async def get_patients(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Patient]:
        """Get patients with optional filters"""
        try:
            query = self.db.query(Patient)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(Patient, field):
                        query = query.filter(getattr(Patient, field) == value)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting patients: {str(e)}")
            raise

    async def create_medical_record(
        self,
        record_data: MedicalRecordCreate
    ) -> MedicalRecord:
        """Create a new medical record"""
        try:
            record = MedicalRecord(
                id=str(uuid.uuid4()),
                **record_data.dict()
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            return record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating medical record: {str(e)}")
            raise

    async def create_immunization(
        self,
        immunization_data: ImmunizationCreate
    ) -> Immunization:
        """Create a new immunization record"""
        try:
            immunization = Immunization(
                id=str(uuid.uuid4()),
                **immunization_data.dict()
            )
            
            self.db.add(immunization)
            self.db.commit()
            self.db.refresh(immunization)
            
            return immunization
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating immunization: {str(e)}")
            raise

    async def bulk_import_patients(
        self,
        file_url: str,
        creator_id: str
    ) -> Dict[str, Any]:
        """Import patients from Excel file"""
        try:
            # Download file
            response = requests.get(file_url)
            response.raise_for_status()
            
            # Read Excel file
            df = pd.read_excel(BytesIO(response.content))
            
            # Process records
            total_records = len(df)
            processed_records = 0
            failed_records = 0
            error_log = []
            
            for _, row in df.iterrows():
                try:
                    # Convert row to dict and create patient
                    patient_data = PatientCreate(**row.to_dict())
                    await self.create_patient(patient_data)
                    processed_records += 1
                except Exception as e:
                    failed_records += 1
                    error_log.append({
                        "row": row.to_dict(),
                        "error": str(e)
                    })
            
            return {
                "total_records": total_records,
                "processed_records": processed_records,
                "failed_records": failed_records,
                "error_log": error_log
            }
        except Exception as e:
            logger.error(f"Error in bulk import: {str(e)}")
            raise

    def _check_record_completeness(self, patient: Patient) -> bool:
        """Check if patient record is complete"""
        required_fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'address', 'county', 'sub_county'
        ]
        
        for field in required_fields:
            if not getattr(patient, field):
                return False
        
        return True

    async def get_patient_stats(self) -> Dict[str, Any]:
        """Get patient statistics"""
        try:
            total_patients = self.db.query(Patient).count()
            active_patients = self.db.query(Patient)\
                .filter(Patient.status == PatientStatus.ACTIVE)\
                .count()
            
            # Get patients by county
            county_stats = {}
            counties = self.db.query(Patient.county, Patient.id)\
                .group_by(Patient.county)\
                .all()
            
            for county, _ in counties:
                count = self.db.query(Patient)\
                    .filter(Patient.county == county)\
                    .count()
                county_stats[county] = count
            
            return {
                "total_patients": total_patients,
                "active_patients": active_patients,
                "county_distribution": county_stats
            }
        except Exception as e:
            logger.error(f"Error getting patient stats: {str(e)}")
            raise

    async def search_patients(
        self,
        query: str,
        limit: int = 10
    ) -> List[Patient]:
        """Search patients by name, phone, or NHIF number"""
        try:
            search_query = f"%{query}%"
            return self.db.query(Patient)\
                .filter(
                    or_(
                        Patient.first_name.ilike(search_query),
                        Patient.last_name.ilike(search_query),
                        Patient.phone_number.ilike(search_query),
                        Patient.nhif_number.ilike(search_query)
                    )
                )\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            raise

# Create singleton instance
patient_service = PatientService() 