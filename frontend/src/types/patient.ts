export type Gender = 'male' | 'female' | 'other';
export type PatientStatus = 'active' | 'inactive' | 'deceased' | 'transferred';

export interface Caregiver {
  id: string;
  patient_id: string;
  relationship: 'mother' | 'father' | 'guardian' | 'other';
  first_name: string;
  last_name: string;
  contact_info: {
    phone: string;
    alternative_phone?: string;
    email?: string;
    address?: {
      street: string;
      city: string;
      county: string;
      postal_code?: string;
    };
  };
  demographics: {
    age?: number;
    gender?: 'male' | 'female' | 'other';
    education_level?: string;
    occupation?: string;
    language_preference: string;
  };
  engagement: {
    preferred_contact_method: 'sms' | 'whatsapp' | 'voice' | 'email';
    reminder_preferences: {
      days_before: number[];
      time_of_day: string;
    };
    last_contact_date?: string;
    response_rate: number;
  };
  created_at: string;
  updated_at: string;
  status: 'active' | 'inactive';
}

export interface Patient {
  id: string;
  mrn: string; // Medical Record Number
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  contact_info: {
    phone: string;
    alternative_phone?: string;
    email?: string;
    address: {
      street: string;
      city: string;
      county: string;
      postal_code?: string;
      coordinates?: {
        latitude: number;
        longitude: number;
      };
    };
  };
  demographics: {
    ethnicity?: string;
    language_preference: string;
    education_level?: string;
    occupation?: string;
    insurance_provider?: string;
    insurance_number?: string;
  };
  medical_history: {
    allergies: string[];
    chronic_conditions: string[];
    previous_surgeries: string[];
    family_history: string[];
    current_medications: string[];
  };
  biometrics?: {
    fingerprint_id?: string;
    facial_id?: string;
    photo_url?: string;
  };
  caregivers: Caregiver[];
  created_at: string;
  updated_at: string;
  last_visit_date?: string;
  next_visit_date?: string;
  status: 'active' | 'inactive' | 'deceased';
  flags: {
    incomplete_record: boolean;
    high_risk: boolean;
    special_needs: boolean;
    requires_follow_up: boolean;
  };
}

export interface PatientCreate {
  nhif_number?: string;
  biometric_id?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: Gender;
  nationality: string;
  language_preference: string;
  phone_number: string;
  alternative_phone?: string;
  email?: string;
  address: string;
  county: string;
  sub_county: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  medical_history?: Record<string, any>;
  primary_caregiver?: Omit<Caregiver, 'id' | 'registration_date' | 'last_updated' | 'is_active' | 'metadata'>;
}

export interface PatientUpdate {
  nhif_number?: string;
  biometric_id?: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  gender?: Gender;
  nationality?: string;
  language_preference?: string;
  phone_number?: string;
  alternative_phone?: string;
  email?: string;
  address?: string;
  county?: string;
  sub_county?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  medical_history?: Record<string, any>;
  status?: PatientStatus;
  primary_caregiver_id?: string;
}

export interface MedicalRecord {
  id: string;
  patient_id: string;
  record_type: string;
  record_date: string;
  diagnosis?: string;
  treatment?: string;
  notes?: string;
  attachments?: string[];
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface Immunization {
  id: string;
  patient_id: string;
  vaccine_name: string;
  scheduled_date: string;
  administered_date?: string;
  batch_number?: string;
  administered_by?: string;
  status: string;
  certificate_url?: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface PatientImportResult {
  success: boolean;
  total_records: number;
  imported_records: number;
  failed_records: number;
  errors: {
    row: number;
    error: string;
  }[];
}

export interface PatientSearchParams {
  query: string;
  filters?: {
    status?: Patient['status'];
    age_range?: {
      min: number;
      max: number;
    };
    last_visit_date?: {
      from: string;
      to: string;
    };
    flags?: {
      incomplete_record?: boolean;
      high_risk?: boolean;
      special_needs?: boolean;
      requires_follow_up?: boolean;
    };
  };
  page: number;
  limit: number;
} 