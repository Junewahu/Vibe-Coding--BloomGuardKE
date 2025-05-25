import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import axios from 'axios';
import { Patient, PatientCreate, PatientUpdate, MedicalRecord, Immunization } from '../types/patient';

interface Document {
  id: string;
  patient_id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  uploaded_by: string;
  status: 'pending' | 'verified' | 'rejected';
  notes?: string;
}

interface FollowUp {
  id: string;
  patient_id: string;
  type: 'immunization' | 'milestone' | 'post_operative' | 'chronic_care';
  scheduled_date: string;
  status: 'scheduled' | 'completed' | 'missed' | 'cancelled';
  notes?: string;
  protocol_id?: string;
  reminder_settings: {
    sms: boolean;
    whatsapp: boolean;
    voice: boolean;
    ussd: boolean;
    reminder_days: number[];
  };
}

interface Reminder {
  id: string;
  follow_up_id: string;
  patient_id: string;
  type: 'sms' | 'whatsapp' | 'voice' | 'ussd';
  status: 'pending' | 'sent' | 'delivered' | 'failed';
  scheduled_time: string;
  message_template: string;
  retry_count: number;
  max_retries: number;
  response?: {
    received_at: string;
    action: 'confirmed' | 'cancelled' | 'rescheduled';
    notes?: string;
  };
}

interface Response {
  id: string;
  reminder_id: string;
  patient_id: string;
  received_at: string;
  action: 'confirmed' | 'cancelled' | 'rescheduled';
  channel: 'sms' | 'whatsapp' | 'voice' | 'ussd';
  notes?: string;
  follow_up_id?: string;
}

interface Caregiver {
  id: string;
  patient_id: string;
  name: string;
  relationship: string;
  phone: string;
  email?: string;
  address?: string;
  is_primary: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface CaregiverInteraction {
  id: string;
  caregiver_id: string;
  patient_id: string;
  type: 'visit' | 'call' | 'message' | 'other';
  status: 'scheduled' | 'completed' | 'cancelled' | 'missed';
  scheduled_date: string;
  completed_date?: string;
  notes?: string;
  outcome?: string;
  created_at: string;
  updated_at: string;
}

interface AdherenceMetric {
  id: string;
  patient_id: string;
  type: 'medication' | 'appointment' | 'lifestyle' | 'other';
  target: number;
  achieved: number;
  period: 'daily' | 'weekly' | 'monthly';
  start_date: string;
  end_date?: string;
  status: 'active' | 'completed' | 'cancelled';
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface Incentive {
  id: string;
  patient_id: string;
  type: 'monetary' | 'non_monetary' | 'recognition';
  value: string;
  description: string;
  criteria: {
    metric_type: AdherenceMetric['type'];
    target_value: number;
    period: AdherenceMetric['period'];
  };
  status: 'pending' | 'earned' | 'redeemed' | 'expired';
  earned_at?: string;
  redeemed_at?: string;
  expiry_date?: string;
  created_at: string;
  updated_at: string;
}

interface FieldVisit {
  id: string;
  chw_id: string;
  patient_id: string;
  visit_date: string;
  visit_type: 'scheduled' | 'emergency' | 'follow_up';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  notes: string;
  findings: string;
  recommendations: string;
  created_at: string;
  updated_at: string;
}

interface CHWActivity {
  id: string;
  chw_id: string;
  type: 'visit' | 'training' | 'meeting' | 'other';
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

interface PatientState {
  patients: Patient[];
  currentPatient: Patient | null;
  isLoading: boolean;
  error: string | null;
  createPatient: (data: PatientCreate) => Promise<void>;
  updatePatient: (id: string, data: PatientUpdate) => Promise<void>;
  getPatient: (id: string) => Promise<void>;
  getPatients: () => Promise<void>;
  searchPatients: (query: string) => Promise<void>;
  getMedicalRecords: (patientId: string) => Promise<MedicalRecord[]>;
  createMedicalRecord: (patientId: string, data: Omit<MedicalRecord, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => Promise<void>;
  getImmunizations: (patientId: string) => Promise<Immunization[]>;
  createImmunization: (patientId: string, data: Omit<Immunization, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => Promise<void>;
  getDocuments: (patientId: string) => Promise<Document[]>;
  uploadDocument: (patientId: string, data: FormData) => Promise<void>;
  downloadDocument: (documentId: string) => Promise<Blob>;
  deleteDocument: (documentId: string) => Promise<void>;
  getFollowUps: (patientId: string) => Promise<FollowUp[]>;
  createFollowUp: (patientId: string, data: Omit<FollowUp, 'id' | 'patient_id'>) => Promise<void>;
  updateFollowUp: (followUpId: string, data: Partial<FollowUp>) => Promise<void>;
  deleteFollowUp: (followUpId: string) => Promise<void>;
  getReminders: (patientId: string) => Promise<Reminder[]>;
  createReminder: (patientId: string, data: Omit<Reminder, 'id' | 'patient_id' | 'retry_count' | 'response'>) => Promise<void>;
  updateReminder: (reminderId: string, data: Partial<Reminder>) => Promise<void>;
  deleteReminder: (reminderId: string) => Promise<void>;
  retryReminder: (reminderId: string) => Promise<void>;
  getResponses: (patientId: string) => Promise<Response[]>;
  getResponseStats: (patientId: string) => Promise<{
    total_reminders: number;
    confirmed: number;
    cancelled: number;
    rescheduled: number;
    no_response: number;
    response_rate: number;
    trend: 'up' | 'down' | 'stable';
  }>;
  updateResponse: (responseId: string, data: Partial<Response>) => Promise<void>;
  clearError: () => void;
  caregivers: Caregiver[];
  caregiverInteractions: CaregiverInteraction[];
  loading: {
    caregivers: boolean;
    caregiverInteractions: boolean;
    adherenceMetrics: boolean;
    incentives: boolean;
  };
  error: {
    caregivers: string | null;
    caregiverInteractions: string | null;
    adherenceMetrics: string | null;
    incentives: string | null;
  };
  getCaregivers: (patientId: string) => Promise<void>;
  addCaregiver: (caregiver: Omit<Caregiver, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateCaregiver: (caregiver: Caregiver) => Promise<void>;
  deleteCaregiver: (caregiverId: string) => Promise<void>;
  getCaregiverInteractions: (patientId: string) => Promise<void>;
  scheduleInteraction: (interaction: Omit<CaregiverInteraction, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateInteractionStatus: (interactionId: string, status: CaregiverInteraction['status']) => Promise<void>;
  deleteInteraction: (interactionId: string) => Promise<void>;
  adherenceMetrics: AdherenceMetric[];
  incentives: Incentive[];
  getAdherenceMetrics: (patientId: string) => Promise<void>;
  createAdherenceMetric: (metric: Omit<AdherenceMetric, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateAdherenceMetric: (metricId: string, data: Partial<AdherenceMetric>) => Promise<void>;
  deleteAdherenceMetric: (metricId: string) => Promise<void>;
  getIncentives: (patientId: string) => Promise<void>;
  createIncentive: (incentive: Omit<Incentive, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateIncentive: (incentiveId: string, data: Partial<Incentive>) => Promise<void>;
  deleteIncentive: (incentiveId: string) => Promise<void>;
  redeemIncentive: (incentiveId: string) => Promise<void>;
  fieldVisits: FieldVisit[];
  chwActivities: CHWActivity[];
  loadingFieldVisits: boolean;
  loadingActivities: boolean;
  fieldVisitError: string | null;
  activityError: string | null;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const usePatientStore = create<PatientState>()(
  devtools(
    persist(
      (set, get) => ({
        patients: [],
        currentPatient: null,
        isLoading: false,
        error: null,
        caregivers: [],
        caregiverInteractions: [],
        adherenceMetrics: [],
        incentives: [],
        loading: {
          caregivers: false,
          caregiverInteractions: false,
          adherenceMetrics: false,
          incentives: false,
        },
        error: {
          caregivers: null,
          caregiverInteractions: null,
          adherenceMetrics: null,
          incentives: null,
        },
        fieldVisits: [],
        chwActivities: [],
        loadingFieldVisits: false,
        loadingActivities: false,
        fieldVisitError: null,
        activityError: null,

        createPatient: async (data: PatientCreate) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.post(`${API_URL}/patients`, data);
            set((state) => ({
              patients: [...state.patients, response.data],
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to create patient',
              isLoading: false,
            });
            throw error;
          }
        },

        updatePatient: async (id: string, data: PatientUpdate) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.put(`${API_URL}/patients/${id}`, data);
            set((state) => ({
              patients: state.patients.map((p) =>
                p.id === id ? response.data : p
              ),
              currentPatient: response.data,
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to update patient',
              isLoading: false,
            });
            throw error;
          }
        },

        getPatient: async (id: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${id}`);
            set({
              currentPatient: response.data,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch patient',
              isLoading: false,
            });
            throw error;
          }
        },

        getPatients: async () => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients`);
            set({
              patients: response.data,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch patients',
              isLoading: false,
            });
            throw error;
          }
        },

        searchPatients: async (query: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/search/${query}`);
            set({
              patients: response.data,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to search patients',
              isLoading: false,
            });
            throw error;
          }
        },

        getMedicalRecords: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/medical-records`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch medical records',
              isLoading: false,
            });
            throw error;
          }
        },

        createMedicalRecord: async (patientId: string, data: Omit<MedicalRecord, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/patients/${patientId}/medical-records`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to create medical record',
              isLoading: false,
            });
            throw error;
          }
        },

        getImmunizations: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/immunizations`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch immunizations',
              isLoading: false,
            });
            throw error;
          }
        },

        createImmunization: async (patientId: string, data: Omit<Immunization, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/patients/${patientId}/immunizations`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to create immunization record',
              isLoading: false,
            });
            throw error;
          }
        },

        getDocuments: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/documents`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch documents',
              isLoading: false,
            });
            throw error;
          }
        },

        uploadDocument: async (patientId: string, data: FormData) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/patients/${patientId}/documents`, data, {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            });
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to upload document',
              isLoading: false,
            });
            throw error;
          }
        },

        downloadDocument: async (documentId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/documents/${documentId}/download`, {
              responseType: 'blob',
            });
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to download document',
              isLoading: false,
            });
            throw error;
          }
        },

        deleteDocument: async (documentId: string) => {
          try {
            set({ isLoading: true, error: null });
            await axios.delete(`${API_URL}/documents/${documentId}`);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to delete document',
              isLoading: false,
            });
            throw error;
          }
        },

        getFollowUps: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/follow-ups`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch follow-ups',
              isLoading: false,
            });
            throw error;
          }
        },

        createFollowUp: async (patientId: string, data: Omit<FollowUp, 'id' | 'patient_id'>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/patients/${patientId}/follow-ups`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to create follow-up',
              isLoading: false,
            });
            throw error;
          }
        },

        updateFollowUp: async (followUpId: string, data: Partial<FollowUp>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.put(`${API_URL}/follow-ups/${followUpId}`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to update follow-up',
              isLoading: false,
            });
            throw error;
          }
        },

        deleteFollowUp: async (followUpId: string) => {
          try {
            set({ isLoading: true, error: null });
            await axios.delete(`${API_URL}/follow-ups/${followUpId}`);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to delete follow-up',
              isLoading: false,
            });
            throw error;
          }
        },

        getReminders: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/reminders`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch reminders',
              isLoading: false,
            });
            throw error;
          }
        },

        createReminder: async (patientId: string, data: Omit<Reminder, 'id' | 'patient_id' | 'retry_count' | 'response'>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/patients/${patientId}/reminders`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to create reminder',
              isLoading: false,
            });
            throw error;
          }
        },

        updateReminder: async (reminderId: string, data: Partial<Reminder>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.put(`${API_URL}/reminders/${reminderId}`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to update reminder',
              isLoading: false,
            });
            throw error;
          }
        },

        deleteReminder: async (reminderId: string) => {
          try {
            set({ isLoading: true, error: null });
            await axios.delete(`${API_URL}/reminders/${reminderId}`);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to delete reminder',
              isLoading: false,
            });
            throw error;
          }
        },

        retryReminder: async (reminderId: string) => {
          try {
            set({ isLoading: true, error: null });
            await axios.post(`${API_URL}/reminders/${reminderId}/retry`);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to retry reminder',
              isLoading: false,
            });
            throw error;
          }
        },

        getResponses: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/responses`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch responses',
              isLoading: false,
            });
            throw error;
          }
        },

        getResponseStats: async (patientId: string) => {
          try {
            set({ isLoading: true, error: null });
            const response = await axios.get(`${API_URL}/patients/${patientId}/response-stats`);
            set({ isLoading: false });
            return response.data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch response stats',
              isLoading: false,
            });
            throw error;
          }
        },

        updateResponse: async (responseId: string, data: Partial<Response>) => {
          try {
            set({ isLoading: true, error: null });
            await axios.put(`${API_URL}/responses/${responseId}`, data);
            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to update response',
              isLoading: false,
            });
            throw error;
          }
        },

        clearError: () => set({ error: null }),

        getCaregivers: async (patientId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, caregivers: true } }));
            const response = await axios.get(`${API_URL}/patients/${patientId}/caregivers`);
            set(state => ({
              caregivers: response.data,
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: 'Failed to fetch caregivers' },
            }));
          }
        },

        addCaregiver: async (caregiver) => {
          try {
            set(state => ({ loading: { ...state.loading, caregivers: true } }));
            const response = await axios.post(`${API_URL}/patients/${caregiver.patient_id}/caregivers`, caregiver);
            set(state => ({
              caregivers: [...state.caregivers, response.data],
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: 'Failed to add caregiver' },
            }));
          }
        },

        updateCaregiver: async (caregiver) => {
          try {
            set(state => ({ loading: { ...state.loading, caregivers: true } }));
            const response = await axios.put(`${API_URL}/caregivers/${caregiver.id}`, caregiver);
            set(state => ({
              caregivers: state.caregivers.map(c => c.id === caregiver.id ? response.data : c),
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: 'Failed to update caregiver' },
            }));
          }
        },

        deleteCaregiver: async (caregiverId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, caregivers: true } }));
            await axios.delete(`${API_URL}/caregivers/${caregiverId}`);
            set(state => ({
              caregivers: state.caregivers.filter(c => c.id !== caregiverId),
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregivers: false },
              error: { ...state.error, caregivers: 'Failed to delete caregiver' },
            }));
          }
        },

        getCaregiverInteractions: async (patientId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, caregiverInteractions: true } }));
            const response = await axios.get(`${API_URL}/patients/${patientId}/caregiver-interactions`);
            set(state => ({
              caregiverInteractions: response.data,
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: 'Failed to fetch interactions' },
            }));
          }
        },

        scheduleInteraction: async (interaction) => {
          try {
            set(state => ({ loading: { ...state.loading, caregiverInteractions: true } }));
            const response = await axios.post(`${API_URL}/patients/${interaction.patient_id}/caregiver-interactions`, interaction);
            set(state => ({
              caregiverInteractions: [...state.caregiverInteractions, response.data],
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: 'Failed to schedule interaction' },
            }));
          }
        },

        updateInteractionStatus: async (interactionId: string, status: CaregiverInteraction['status']) => {
          try {
            set(state => ({ loading: { ...state.loading, caregiverInteractions: true } }));
            const response = await axios.patch(`${API_URL}/caregiver-interactions/${interactionId}/status`, { status });
            set(state => ({
              caregiverInteractions: state.caregiverInteractions.map(i => 
                i.id === interactionId ? response.data : i
              ),
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: 'Failed to update interaction status' },
            }));
          }
        },

        deleteInteraction: async (interactionId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, caregiverInteractions: true } }));
            await axios.delete(`${API_URL}/caregiver-interactions/${interactionId}`);
            set(state => ({
              caregiverInteractions: state.caregiverInteractions.filter(i => i.id !== interactionId),
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, caregiverInteractions: false },
              error: { ...state.error, caregiverInteractions: 'Failed to delete interaction' },
            }));
          }
        },

        getAdherenceMetrics: async (patientId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, adherenceMetrics: true } }));
            const response = await axios.get(`${API_URL}/patients/${patientId}/adherence-metrics`);
            set(state => ({
              adherenceMetrics: response.data,
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: 'Failed to fetch adherence metrics' },
            }));
          }
        },

        createAdherenceMetric: async (metric) => {
          try {
            set(state => ({ loading: { ...state.loading, adherenceMetrics: true } }));
            const response = await axios.post(`${API_URL}/patients/${metric.patient_id}/adherence-metrics`, metric);
            set(state => ({
              adherenceMetrics: [...state.adherenceMetrics, response.data],
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: 'Failed to create adherence metric' },
            }));
          }
        },

        updateAdherenceMetric: async (metricId: string, data) => {
          try {
            set(state => ({ loading: { ...state.loading, adherenceMetrics: true } }));
            const response = await axios.put(`${API_URL}/adherence-metrics/${metricId}`, data);
            set(state => ({
              adherenceMetrics: state.adherenceMetrics.map(m => m.id === metricId ? response.data : m),
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: 'Failed to update adherence metric' },
            }));
          }
        },

        deleteAdherenceMetric: async (metricId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, adherenceMetrics: true } }));
            await axios.delete(`${API_URL}/adherence-metrics/${metricId}`);
            set(state => ({
              adherenceMetrics: state.adherenceMetrics.filter(m => m.id !== metricId),
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, adherenceMetrics: false },
              error: { ...state.error, adherenceMetrics: 'Failed to delete adherence metric' },
            }));
          }
        },

        getIncentives: async (patientId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, incentives: true } }));
            const response = await axios.get(`${API_URL}/patients/${patientId}/incentives`);
            set(state => ({
              incentives: response.data,
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: 'Failed to fetch incentives' },
            }));
          }
        },

        createIncentive: async (incentive) => {
          try {
            set(state => ({ loading: { ...state.loading, incentives: true } }));
            const response = await axios.post(`${API_URL}/patients/${incentive.patient_id}/incentives`, incentive);
            set(state => ({
              incentives: [...state.incentives, response.data],
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: 'Failed to create incentive' },
            }));
          }
        },

        updateIncentive: async (incentiveId: string, data) => {
          try {
            set(state => ({ loading: { ...state.loading, incentives: true } }));
            const response = await axios.put(`${API_URL}/incentives/${incentiveId}`, data);
            set(state => ({
              incentives: state.incentives.map(i => i.id === incentiveId ? response.data : i),
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: 'Failed to update incentive' },
            }));
          }
        },

        deleteIncentive: async (incentiveId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, incentives: true } }));
            await axios.delete(`${API_URL}/incentives/${incentiveId}`);
            set(state => ({
              incentives: state.incentives.filter(i => i.id !== incentiveId),
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: 'Failed to delete incentive' },
            }));
          }
        },

        redeemIncentive: async (incentiveId: string) => {
          try {
            set(state => ({ loading: { ...state.loading, incentives: true } }));
            const response = await axios.post(`${API_URL}/incentives/${incentiveId}/redeem`);
            set(state => ({
              incentives: state.incentives.map(i => i.id === incentiveId ? response.data : i),
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: null },
            }));
          } catch (error) {
            set(state => ({
              loading: { ...state.loading, incentives: false },
              error: { ...state.error, incentives: 'Failed to redeem incentive' },
            }));
          }
        },

        getFieldVisits: async (chwId: string) => {
          set({ loadingFieldVisits: true, fieldVisitError: null });
          try {
            const response = await axios.get(`${API_URL}/api/chw/${chwId}/visits`);
            set({ fieldVisits: response.data, loadingFieldVisits: false });
          } catch (error) {
            set({ 
              fieldVisitError: 'Failed to load field visits', 
              loadingFieldVisits: false 
            });
          }
        },

        getCHWActivities: async (chwId: string) => {
          set({ loadingActivities: true, activityError: null });
          try {
            const response = await axios.get(`${API_URL}/api/chw/${chwId}/activities`);
            set({ chwActivities: response.data, loadingActivities: false });
          } catch (error) {
            set({ 
              activityError: 'Failed to load activities', 
              loadingActivities: false 
            });
          }
        },

        createFieldVisit: async (visit: Omit<FieldVisit, 'id' | 'created_at' | 'updated_at'>) => {
          set({ loadingFieldVisits: true, fieldVisitError: null });
          try {
            const response = await axios.post('/api/visits', visit);
            set(state => ({ 
              fieldVisits: [...state.fieldVisits, response.data],
              loadingFieldVisits: false 
            }));
            return response.data;
          } catch (error) {
            set({ 
              fieldVisitError: 'Failed to create field visit', 
              loadingFieldVisits: false 
            });
            throw error;
          }
        },

        updateFieldVisit: async (visitId: string, updates: Partial<FieldVisit>) => {
          set({ loadingFieldVisits: true, fieldVisitError: null });
          try {
            const response = await axios.patch(`/api/visits/${visitId}`, updates);
            set(state => ({
              fieldVisits: state.fieldVisits.map(v => 
                v.id === visitId ? response.data : v
              ),
              loadingFieldVisits: false
            }));
            return response.data;
          } catch (error) {
            set({ 
              fieldVisitError: 'Failed to update field visit', 
              loadingFieldVisits: false 
            });
            throw error;
          }
        },

        createCHWActivity: async (activity: Omit<CHWActivity, 'id' | 'created_at' | 'updated_at'>) => {
          set({ loadingActivities: true, activityError: null });
          try {
            const response = await axios.post('/api/activities', activity);
            set(state => ({ 
              chwActivities: [...state.chwActivities, response.data],
              loadingActivities: false 
            }));
            return response.data;
          } catch (error) {
            set({ 
              activityError: 'Failed to create activity', 
              loadingActivities: false 
            });
            throw error;
          }
        },
      }),
      {
        name: 'patient-storage',
        partialize: (state) => ({
          patients: state.patients,
          currentPatient: state.currentPatient,
          caregivers: state.caregivers,
          caregiverInteractions: state.caregiverInteractions,
          adherenceMetrics: state.adherenceMetrics,
          incentives: state.incentives,
          fieldVisits: state.fieldVisits,
          chwActivities: state.chwActivities,
          loadingFieldVisits: state.loadingFieldVisits,
          loadingActivities: state.loadingActivities,
          fieldVisitError: state.fieldVisitError,
          activityError: state.activityError,
        }),
      }
    )
  )
); 