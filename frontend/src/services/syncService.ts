import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { settingsService } from './settingsService';

interface SyncQueueItem {
  id: string;
  type: 'patient' | 'appointment' | 'reminder' | 'visit';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  retryCount: number;
}

interface BloomGuardDB extends DBSchema {
  syncQueue: {
    key: string;
    value: SyncQueueItem;
  };
  patients: {
    key: string;
    value: any;
  };
  appointments: {
    key: string;
    value: any;
  };
  reminders: {
    key: string;
    value: any;
  };
  visits: {
    key: string;
    value: any;
  };
  offlineData: {
    key: string;
    value: any;
  };
}

class SyncService {
  private static instance: SyncService;
  private db: IDBPDatabase<BloomGuardDB> | null = null;
  private syncInProgress = false;
  private maxRetries = 3;
  private syncInterval = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    this.initDB();
  }

  public static getInstance(): SyncService {
    if (!SyncService.instance) {
      SyncService.instance = new SyncService();
    }
    return SyncService.instance;
  }

  private async initDB() {
    try {
      this.db = await openDB<BloomGuardDB>('bloomguard', 1, {
        upgrade(db) {
          // Create object stores
          db.createObjectStore('syncQueue', { keyPath: 'id' });
          db.createObjectStore('patients', { keyPath: 'id' });
          db.createObjectStore('appointments', { keyPath: 'id' });
          db.createObjectStore('reminders', { keyPath: 'id' });
          db.createObjectStore('visits', { keyPath: 'id' });
          db.createObjectStore('offlineData', { keyPath: 'key' });
        },
      });
    } catch (error) {
      console.error('Failed to initialize IndexedDB:', error);
      throw error;
    }
  }

  public async addToSyncQueue(item: Omit<SyncQueueItem, 'id' | 'timestamp' | 'retryCount'>) {
    if (!this.db) throw new Error('Database not initialized');

    const syncItem: SyncQueueItem = {
      ...item,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      retryCount: 0,
    };

    await this.db.add('syncQueue', syncItem);
    this.triggerSync();
  }

  public async getSyncStatus() {
    if (!this.db) throw new Error('Database not initialized');

    const queue = await this.db.getAll('syncQueue');
    const pendingCount = queue.length;
    const lastSync = localStorage.getItem('lastSync');
    const isOnline = navigator.onLine;

    return {
      pendingCount,
      lastSync: lastSync ? new Date(lastSync) : null,
      isOnline,
      syncInProgress: this.syncInProgress,
    };
  }

  public async triggerSync() {
    if (this.syncInProgress || !navigator.onLine) return;

    this.syncInProgress = true;
    try {
      await this.processSyncQueue();
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  private async processSyncQueue() {
    if (!this.db) throw new Error('Database not initialized');

    const queue = await this.db.getAll('syncQueue');
    for (const item of queue) {
      try {
        await this.processQueueItem(item);
        await this.db.delete('syncQueue', item.id);
      } catch (error) {
        console.error(`Failed to process queue item ${item.id}:`, error);
        if (item.retryCount < this.maxRetries) {
          await this.db.put('syncQueue', {
            ...item,
            retryCount: item.retryCount + 1,
          });
        }
      }
    }

    localStorage.setItem('lastSync', new Date().toISOString());
  }

  private async processQueueItem(item: SyncQueueItem) {
    // Process different types of sync items
    switch (item.type) {
      case 'patient':
        await this.syncPatient(item);
        break;
      case 'appointment':
        await this.syncAppointment(item);
        break;
      case 'reminder':
        await this.syncReminder(item);
        break;
      case 'visit':
        await this.syncVisit(item);
        break;
      default:
        throw new Error(`Unknown sync item type: ${item.type}`);
    }
  }

  private async syncPatient(item: SyncQueueItem) {
    const endpoint = '/api/patients';
    const { action, data } = item;

    switch (action) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'update':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'delete':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'DELETE',
        });
        break;
    }
  }

  private async syncAppointment(item: SyncQueueItem) {
    const endpoint = '/api/appointments';
    const { action, data } = item;

    switch (action) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'update':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'delete':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'DELETE',
        });
        break;
    }
  }

  private async syncReminder(item: SyncQueueItem) {
    const endpoint = '/api/reminders';
    const { action, data } = item;

    switch (action) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'update':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'delete':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'DELETE',
        });
        break;
    }
  }

  private async syncVisit(item: SyncQueueItem) {
    const endpoint = '/api/visits';
    const { action, data } = item;

    switch (action) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'update':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        break;
      case 'delete':
        await fetch(`${endpoint}/${data.id}`, {
          method: 'DELETE',
        });
        break;
    }
  }

  public startAutoSync() {
    setInterval(() => this.triggerSync(), this.syncInterval);
  }

  public async clearSyncQueue() {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.clear('syncQueue');
  }

  public async saveOfflineData(key: string, data: any) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.put('offlineData', data, key);
  }

  public async getOfflineData(key: string) {
    if (!this.db) throw new Error('Database not initialized');
    return this.db.get('offlineData', key);
  }

  public async clearOfflineData(key: string) {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.delete('offlineData', key);
  }
}

export const syncService = SyncService.getInstance(); 