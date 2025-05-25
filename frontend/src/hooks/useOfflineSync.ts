import { useEffect, useState } from 'react';
import { offlineSync } from '../services/offlineSync';

export const useOfflineSync = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInitialized, setIsInitialized] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'error'>('idle');

  useEffect(() => {
    const initializeOfflineSync = async () => {
      try {
        await offlineSync.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize offline sync:', error);
        setSyncStatus('error');
      }
    };

    initializeOfflineSync();

    const handleOnline = () => {
      setIsOnline(true);
      offlineSync.syncPendingChanges();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      offlineSync.cleanup();
    };
  }, []);

  const syncNow = async () => {
    if (!isOnline) {
      throw new Error('Cannot sync while offline');
    }

    try {
      setSyncStatus('syncing');
      await offlineSync.syncPendingChanges();
      setSyncStatus('idle');
    } catch (error) {
      console.error('Failed to sync:', error);
      setSyncStatus('error');
      throw error;
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