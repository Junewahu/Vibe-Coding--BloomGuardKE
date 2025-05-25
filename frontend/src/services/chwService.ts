import { apiGateway, API_ENDPOINTS } from './apiGateway';
import { FieldVisit, CHWActivity } from '../types/chw';

export const chwService = {
  // Field Visits
  getFieldVisits: async (chwId: string): Promise<FieldVisit[]> => {
    return apiGateway.get<FieldVisit[]>(API_ENDPOINTS.CHW.VISITS(chwId));
  },

  createFieldVisit: async (visit: Omit<FieldVisit, 'id' | 'created_at' | 'updated_at'>): Promise<FieldVisit> => {
    return apiGateway.post<FieldVisit>(API_ENDPOINTS.CHW.VISITS(visit.chw_id), visit);
  },

  updateFieldVisit: async (visitId: string, updates: Partial<FieldVisit>): Promise<FieldVisit> => {
    return apiGateway.patch<FieldVisit>(`/visits/${visitId}`, updates);
  },

  deleteFieldVisit: async (visitId: string): Promise<void> => {
    return apiGateway.delete(`/visits/${visitId}`);
  },

  // CHW Activities
  getCHWActivities: async (chwId: string): Promise<CHWActivity[]> => {
    return apiGateway.get<CHWActivity[]>(API_ENDPOINTS.CHW.ACTIVITIES(chwId));
  },

  createCHWActivity: async (activity: Omit<CHWActivity, 'id' | 'created_at' | 'updated_at'>): Promise<CHWActivity> => {
    return apiGateway.post<CHWActivity>(API_ENDPOINTS.CHW.ACTIVITIES(activity.chw_id), activity);
  },

  updateCHWActivity: async (activityId: string, updates: Partial<CHWActivity>): Promise<CHWActivity> => {
    return apiGateway.patch<CHWActivity>(`/activities/${activityId}`, updates);
  },

  deleteCHWActivity: async (activityId: string): Promise<void> => {
    return apiGateway.delete(`/activities/${activityId}`);
  },

  // Statistics
  getCHWStats: async (chwId: string): Promise<{
    totalVisits: number;
    completedVisits: number;
    scheduledActivities: number;
    visitTrend: number;
  }> => {
    return apiGateway.get(`/chw/${chwId}/stats`);
  },
}; 