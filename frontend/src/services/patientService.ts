import { apiGateway, API_ENDPOINTS } from './apiGateway';
import { Patient, Caregiver, PatientImportResult, PatientSearchParams } from '../types/patient';
import { InternalAxiosRequestConfig } from 'axios';

export const patientService = {
  // Patient Management
  getPatients: async (params: PatientSearchParams) => {
    return apiGateway.get<{ patients: Patient[]; total: number }>(
      API_ENDPOINTS.PATIENTS.SEARCH,
      { params } as InternalAxiosRequestConfig
    );
  },

  getPatient: async (id: string) => {
    return apiGateway.get<Patient>(`${API_ENDPOINTS.PATIENTS.BASE}/${id}`);
  },

  createPatient: async (patient: Omit<Patient, 'id' | 'created_at' | 'updated_at'>) => {
    return apiGateway.post<Patient>(API_ENDPOINTS.PATIENTS.BASE, patient);
  },

  updatePatient: async (id: string, updates: Partial<Patient>) => {
    return apiGateway.patch<Patient>(`${API_ENDPOINTS.PATIENTS.BASE}/${id}`, updates);
  },

  deletePatient: async (id: string) => {
    return apiGateway.delete(`${API_ENDPOINTS.PATIENTS.BASE}/${id}`);
  },

  // Bulk Import
  importPatients: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiGateway.post<PatientImportResult>(
      `${API_ENDPOINTS.PATIENTS.BASE}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      } as InternalAxiosRequestConfig
    );
  },

  // Caregiver Management
  getCaregivers: async (patientId: string) => {
    return apiGateway.get<Caregiver[]>(API_ENDPOINTS.PATIENTS.CAREGIVERS(patientId));
  },

  addCaregiver: async (patientId: string, caregiver: Omit<Caregiver, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => {
    return apiGateway.post<Caregiver>(API_ENDPOINTS.PATIENTS.CAREGIVERS(patientId), caregiver);
  },

  updateCaregiver: async (patientId: string, caregiverId: string, updates: Partial<Caregiver>) => {
    return apiGateway.patch<Caregiver>(
      `${API_ENDPOINTS.PATIENTS.CAREGIVERS(patientId)}/${caregiverId}`,
      updates
    );
  },

  removeCaregiver: async (patientId: string, caregiverId: string) => {
    return apiGateway.delete(`${API_ENDPOINTS.PATIENTS.CAREGIVERS(patientId)}/${caregiverId}`);
  },

  // Medical Records
  getMedicalRecords: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.MEDICAL_RECORDS(patientId)}`);
  },

  // Immunizations
  getImmunizations: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.IMMUNIZATIONS(patientId)}`);
  },

  // Documents
  getDocuments: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.DOCUMENTS(patientId)}`);
  },

  uploadDocument: async (patientId: string, file: File, metadata: { type: string; description: string }) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    return apiGateway.post(
      `${API_ENDPOINTS.PATIENTS.DOCUMENTS(patientId)}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      } as InternalAxiosRequestConfig
    );
  },

  // Follow-ups
  getFollowUps: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.FOLLOW_UPS(patientId)}`);
  },

  // Reminders
  getReminders: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.REMINDERS(patientId)}`);
  },

  // Responses
  getResponses: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.RESPONSES(patientId)}`);
  },

  // Adherence Metrics
  getAdherenceMetrics: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.ADHERENCE(patientId)}`);
  },

  // Incentives
  getIncentives: async (patientId: string) => {
    return apiGateway.get(`${API_ENDPOINTS.PATIENTS.INCENTIVES(patientId)}`);
  },
}; 