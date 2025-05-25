import { useState, useCallback } from 'react';
import { useToast } from '@chakra-ui/react';
import { patientService } from '../services/patientService';
import { Patient, Caregiver, PatientSearchParams } from '../types/patient';

export const usePatient = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [caregivers, setCaregivers] = useState<Caregiver[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalPatients, setTotalPatients] = useState(0);
  const toast = useToast();

  const searchPatients = useCallback(async (params: PatientSearchParams) => {
    try {
      setIsLoading(true);
      const response = await patientService.getPatients(params);
      setPatients(response.patients);
      setTotalPatients(response.total);
    } catch (error) {
      toast({
        title: 'Error searching patients',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const getPatient = useCallback(async (id: string) => {
    try {
      setIsLoading(true);
      const patient = await patientService.getPatient(id);
      setSelectedPatient(patient);
      return patient;
    } catch (error) {
      toast({
        title: 'Error fetching patient',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const createPatient = useCallback(async (patient: Omit<Patient, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      setIsLoading(true);
      const newPatient = await patientService.createPatient(patient);
      setPatients(prev => [...prev, newPatient]);
      toast({
        title: 'Patient created successfully',
        status: 'success',
        duration: 3000,
      });
      return newPatient;
    } catch (error) {
      toast({
        title: 'Error creating patient',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const updatePatient = useCallback(async (id: string, updates: Partial<Patient>) => {
    try {
      setIsLoading(true);
      const updatedPatient = await patientService.updatePatient(id, updates);
      setPatients(prev => prev.map(patient => 
        patient.id === id ? updatedPatient : patient
      ));
      if (selectedPatient?.id === id) {
        setSelectedPatient(updatedPatient);
      }
      toast({
        title: 'Patient updated successfully',
        status: 'success',
        duration: 3000,
      });
      return updatedPatient;
    } catch (error) {
      toast({
        title: 'Error updating patient',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [selectedPatient, toast]);

  const deletePatient = useCallback(async (id: string) => {
    try {
      setIsLoading(true);
      await patientService.deletePatient(id);
      setPatients(prev => prev.filter(patient => patient.id !== id));
      if (selectedPatient?.id === id) {
        setSelectedPatient(null);
      }
      toast({
        title: 'Patient deleted successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error deleting patient',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [selectedPatient, toast]);

  const importPatients = useCallback(async (file: File) => {
    try {
      setIsLoading(true);
      const result = await patientService.importPatients(file);
      if (result.success) {
        toast({
          title: 'Patients imported successfully',
          description: `Imported ${result.imported_records} of ${result.total_records} records`,
          status: 'success',
          duration: 5000,
        });
      } else {
        toast({
          title: 'Import partially successful',
          description: `Failed to import ${result.failed_records} records`,
          status: 'warning',
          duration: 5000,
        });
      }
      return result;
    } catch (error) {
      toast({
        title: 'Error importing patients',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const loadCaregivers = useCallback(async (patientId: string) => {
    try {
      setIsLoading(true);
      const caregivers = await patientService.getCaregivers(patientId);
      setCaregivers(caregivers);
      return caregivers;
    } catch (error) {
      toast({
        title: 'Error loading caregivers',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const addCaregiver = useCallback(async (patientId: string, caregiver: Omit<Caregiver, 'id' | 'patient_id' | 'created_at' | 'updated_at'>) => {
    try {
      setIsLoading(true);
      const newCaregiver = await patientService.addCaregiver(patientId, caregiver);
      setCaregivers(prev => [...prev, newCaregiver]);
      toast({
        title: 'Caregiver added successfully',
        status: 'success',
        duration: 3000,
      });
      return newCaregiver;
    } catch (error) {
      toast({
        title: 'Error adding caregiver',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const updateCaregiver = useCallback(async (patientId: string, caregiverId: string, updates: Partial<Caregiver>) => {
    try {
      setIsLoading(true);
      const updatedCaregiver = await patientService.updateCaregiver(patientId, caregiverId, updates);
      setCaregivers(prev => prev.map(caregiver => 
        caregiver.id === caregiverId ? updatedCaregiver : caregiver
      ));
      toast({
        title: 'Caregiver updated successfully',
        status: 'success',
        duration: 3000,
      });
      return updatedCaregiver;
    } catch (error) {
      toast({
        title: 'Error updating caregiver',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const removeCaregiver = useCallback(async (patientId: string, caregiverId: string) => {
    try {
      setIsLoading(true);
      await patientService.removeCaregiver(patientId, caregiverId);
      setCaregivers(prev => prev.filter(caregiver => caregiver.id !== caregiverId));
      toast({
        title: 'Caregiver removed successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error removing caregiver',
        status: 'error',
        duration: 3000,
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    patients,
    selectedPatient,
    caregivers,
    isLoading,
    totalPatients,
    searchPatients,
    getPatient,
    createPatient,
    updatePatient,
    deletePatient,
    importPatients,
    loadCaregivers,
    addCaregiver,
    updateCaregiver,
    removeCaregiver,
  };
}; 