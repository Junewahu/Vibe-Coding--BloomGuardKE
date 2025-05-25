import { useState, useCallback } from 'react';
import { useToast } from '@chakra-ui/react';
import { chwService } from '../services/chwService';
import { FieldVisit, CHWActivity } from '../types/chw';

export const useCHW = (chwId: string) => {
  const [fieldVisits, setFieldVisits] = useState<FieldVisit[]>([]);
  const [activities, setActivities] = useState<CHWActivity[]>([]);
  const [stats, setStats] = useState({
    totalVisits: 0,
    completedVisits: 0,
    scheduledActivities: 0,
    visitTrend: 0,
  });
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const loadFieldData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [visits, chwActivities, chwStats] = await Promise.all([
        chwService.getFieldVisits(chwId),
        chwService.getCHWActivities(chwId),
        chwService.getCHWStats(chwId),
      ]);

      setFieldVisits(visits);
      setActivities(chwActivities);
      setStats(chwStats);
    } catch (error) {
      toast({
        title: 'Error loading field data',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  }, [chwId, toast]);

  const createFieldVisit = useCallback(async (visit: Omit<FieldVisit, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const newVisit = await chwService.createFieldVisit(visit);
      setFieldVisits(prev => [...prev, newVisit]);
      toast({
        title: 'Visit scheduled successfully',
        status: 'success',
        duration: 3000,
      });
      return newVisit;
    } catch (error) {
      toast({
        title: 'Error scheduling visit',
        status: 'error',
        duration: 3000,
      });
      throw error;
    }
  }, [toast]);

  const updateFieldVisit = useCallback(async (visitId: string, updates: Partial<FieldVisit>) => {
    try {
      const updatedVisit = await chwService.updateFieldVisit(visitId, updates);
      setFieldVisits(prev => prev.map(visit => 
        visit.id === visitId ? updatedVisit : visit
      ));
      toast({
        title: 'Visit updated successfully',
        status: 'success',
        duration: 3000,
      });
      return updatedVisit;
    } catch (error) {
      toast({
        title: 'Error updating visit',
        status: 'error',
        duration: 3000,
      });
      throw error;
    }
  }, [toast]);

  const createCHWActivity = useCallback(async (activity: Omit<CHWActivity, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const newActivity = await chwService.createCHWActivity(activity);
      setActivities(prev => [...prev, newActivity]);
      toast({
        title: 'Activity created successfully',
        status: 'success',
        duration: 3000,
      });
      return newActivity;
    } catch (error) {
      toast({
        title: 'Error creating activity',
        status: 'error',
        duration: 3000,
      });
      throw error;
    }
  }, [toast]);

  const updateCHWActivity = useCallback(async (activityId: string, updates: Partial<CHWActivity>) => {
    try {
      const updatedActivity = await chwService.updateCHWActivity(activityId, updates);
      setActivities(prev => prev.map(activity => 
        activity.id === activityId ? updatedActivity : activity
      ));
      toast({
        title: 'Activity updated successfully',
        status: 'success',
        duration: 3000,
      });
      return updatedActivity;
    } catch (error) {
      toast({
        title: 'Error updating activity',
        status: 'error',
        duration: 3000,
      });
      throw error;
    }
  }, [toast]);

  return {
    fieldVisits,
    activities,
    stats,
    isLoading,
    loadFieldData,
    createFieldVisit,
    updateFieldVisit,
    createCHWActivity,
    updateCHWActivity,
  };
}; 