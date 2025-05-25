import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { Patient, MedicalRecord, Immunization, Document, FollowUp, Reminder, Response } from '../types/patient';

interface BloomGuardDB extends DBSchema {
  patients: {
    key: string;
    value: Patient;
    indexes: { 'by-name': string };
  };
  medicalRecords: {
    key: string;
    value: MedicalRecord;
    indexes: { 'by-patient': string };
  };
  immunizations: {
    key: string;
    value: Immunization;
    indexes: { 'by-patient': string };
  };
  documents: {
    key: string;
    value: Document;
    indexes: { 'by-patient': string };
  };
  followUps: {
    key: string;
    value: FollowUp;
    indexes: { 'by-patient': string };
  };
  reminders: {
    key: string;
    value: Reminder;
    indexes: { 'by-patient': string };
  };
  responses: {
    key: string;
    value: Response;
    indexes: { 'by-patient': string };
  };
  syncQueue: {
    key: string;
    value: {
      id: string;
      action: 'create' | 'update' | 'delete';
      entity: string;
      data: any;
      timestamp: number;
      status: 'pending' | 'syncing' | 'completed' | 'failed';
      retryCount: number;
    };
  };
}

class OfflineSyncService {
  private db: IDBPDatabase<BloomGuardDB> | null = null;
  private syncInProgress = false;
  private syncInterval: NodeJS.Timeout | null = null;

  async initialize() {
    try {
      this.db = await openDB<BloomGuardDB>('bloomguard-offline', 1, {
        upgrade(db) {
          // Create object stores
          const patientStore = db.createObjectStore('patients', { keyPath: 'id' });
          patientStore.createIndex('by-name', 'name');

          const medicalRecordStore = db.createObjectStore('medicalRecords', { keyPath: 'id' });
          medicalRecordStore.createIndex('by-patient', 'patient_id');

          const immunizationStore = db.createObjectStore('immunizations', { keyPath: 'id' });
          immunizationStore.createIndex('by-patient', 'patient_id');

          const documentStore = db.createObjectStore('documents', { keyPath: 'id' });
          documentStore.createIndex('by-patient', 'patient_id');

          const followUpStore = db.createObjectStore('followUps', { keyPath: 'id' });
          followUpStore.createIndex('by-patient', 'patient_id');

          const reminderStore = db.createObjectStore('reminders', { keyPath: 'id' });
          reminderStore.createIndex('by-patient', 'patient_id');

          const responseStore = db.createObjectStore('responses', { keyPath: 'id' });
          responseStore.createIndex('by-patient', 'patient_id');

          const syncQueueStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
        },
      });

      // Start periodic sync
      this.startPeriodicSync();
    } catch (error) {
      console.error('Failed to initialize offline sync:', error);
      throw error;
    }
  }

  private startPeriodicSync() {
    // Sync every 5 minutes if online
    this.syncInterval = setInterval(() => {
      if (navigator.onLine && !this.syncInProgress) {
        this.syncPendingChanges();
      }
    }, 5 * 60 * 1000);
  }

  async addToSyncQueue(action: 'create' | 'update' | 'delete', entity: string, data: any) {
    if (!this.db) throw new Error('Database not initialized');

    const queueItem = {
      id: `${entity}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      action,
      entity,
      data,
      timestamp: Date.now(),
      status: 'pending',
      retryCount: 0,
    };

    await this.db.add('syncQueue', queueItem);
  }

  async syncPendingChanges() {
    if (!this.db || this.syncInProgress) return;

    try {
      this.syncInProgress = true;
      const pendingItems = await this.db.getAllFromIndex('syncQueue', 'status', 'pending');

      for (const item of pendingItems) {
        try {
          await this.processSyncItem(item);
          await this.db.put('syncQueue', { ...item, status: 'completed' });
        } catch (error) {
          console.error(`Failed to sync item ${item.id}:`, error);
          await this.handleSyncError(item);
        }
      }
    } finally {
      this.syncInProgress = false;
    }
  }

  private async processSyncItem(item: any) {
    // TODO: Implement actual API calls based on the sync item
    // This would involve making the appropriate API request based on the action and entity
    console.log('Processing sync item:', item);
  }

  private async handleSyncError(item: any) {
    if (!this.db) return;

    const updatedItem = {
      ...item,
      retryCount: item.retryCount + 1,
      status: item.retryCount >= 3 ? 'failed' : 'pending',
    };

    await this.db.put('syncQueue', updatedItem);
  }

  // Offline-first data operations
  async getPatient(id: string): Promise<Patient | undefined> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.get('patients', id);
  }

  async getMedicalRecords(patientId: string): Promise<MedicalRecord[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('medicalRecords', 'by-patient', patientId);
  }

  async getImmunizations(patientId: string): Promise<Immunization[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('immunizations', 'by-patient', patientId);
  }

  async getDocuments(patientId: string): Promise<Document[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('documents', 'by-patient', patientId);
  }

  async getFollowUps(patientId: string): Promise<FollowUp[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('followUps', 'by-patient', patientId);
  }

  async getReminders(patientId: string): Promise<Reminder[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('reminders', 'by-patient', patientId);
  }

  async getResponses(patientId: string): Promise<Response[]> {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.getAllFromIndex('responses', 'by-patient', patientId);
  }

  // Data synchronization methods
  async syncPatient(patient: Patient) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('patients', patient);
    await this.addToSyncQueue('update', 'patients', patient);
  }

  async syncMedicalRecord(record: MedicalRecord) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('medicalRecords', record);
    await this.addToSyncQueue('update', 'medicalRecords', record);
  }

  async syncImmunization(immunization: Immunization) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('immunizations', immunization);
    await this.addToSyncQueue('update', 'immunizations', immunization);
  }

  async syncDocument(document: Document) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('documents', document);
    await this.addToSyncQueue('update', 'documents', document);
  }

  async syncFollowUp(followUp: FollowUp) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('followUps', followUp);
    await this.addToSyncQueue('update', 'followUps', followUp);
  }

  async syncReminder(reminder: Reminder) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('reminders', reminder);
    await this.addToSyncQueue('update', 'reminders', reminder);
  }

  async syncResponse(response: Response) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('responses', response);
    await this.addToSyncQueue('update', 'responses', response);
  }

  // Cleanup
  async cleanup() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    if (this.db) {
      this.db.close();
    }
  }
}

export const offlineSync = new OfflineSyncService(); 