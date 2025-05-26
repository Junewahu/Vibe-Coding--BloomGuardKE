import { useState, useEffect } from 'react';
import { useNetwork } from './useNetwork';

interface SyncQueueItem {
  id: string;
  type: string;
  data: any;
  timestamp: number;
}

class OfflineSyncService {
  private queue: SyncQueueItem[] = [];
  private lastSyncTime: number = Date.now();

  constructor() {
    this.loadQueue();
  }

  private loadQueue() {
    const savedQueue = localStorage.getItem('syncQueue');
    if (savedQueue) {
      this.queue = JSON.parse(savedQueue);
    }
  }

  private saveQueue() {
    localStorage.setItem('syncQueue', JSON.stringify(this.queue));
  }

  addToQueue(item: Omit<SyncQueueItem, 'timestamp'>) {
    this.queue.push({
      ...item,
      timestamp: Date.now(),
    });
    this.saveQueue();
  }

  removeFromQueue(id: string) {
    this.queue = this.queue.filter(item => item.id !== id);
    this.saveQueue();
  }

  getQueue() {
    return this.queue;
  }

  clearQueue() {
    this.queue = [];
    this.saveQueue();
  }

  updateLastSyncTime() {
    this.lastSyncTime = Date.now();
    localStorage.setItem('lastSyncTime', this.lastSyncTime.toString());
  }

  getLastSyncTime() {
    return this.lastSyncTime;
  }
}

export const useOfflineSync = () => {
  const { isOnline } = useNetwork();
  const [isInitialized, setIsInitialized] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'error'>('idle');
  const [offlineSync] = useState(() => new OfflineSyncService());

  useEffect(() => {
    setIsInitialized(true);
  }, []);

  const syncNow = async () => {
    if (!isOnline || syncStatus === 'syncing') return;

    try {
      setSyncStatus('syncing');
      const queue = offlineSync.getQueue();

      for (const item of queue) {
        // Implement your sync logic here
        // For example, making API calls for each queued item
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated API call
        offlineSync.removeFromQueue(item.id);
      }

      offlineSync.updateLastSyncTime();
      setSyncStatus('idle');
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncStatus('error');
    }
  };

  return {
    isOnline,
    isInitialized,
    syncStatus,
    syncNow,
    offlineSync,
  };
}; 