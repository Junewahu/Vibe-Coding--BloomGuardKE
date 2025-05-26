import { useState, useEffect } from 'react';

export const useNetwork = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [syncQueue, setSyncQueue] = useState<Array<() => Promise<void>>>([]);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      processSyncQueue();
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const processSyncQueue = async () => {
    if (!isOnline || syncQueue.length === 0) return;

    try {
      const queue = [...syncQueue];
      setSyncQueue([]);

      for (const syncOperation of queue) {
        await syncOperation();
      }

      setLastSyncTime(new Date());
    } catch (error) {
      console.error('Sync queue processing failed:', error);
      // Retry failed operations
      setSyncQueue((prev) => [...prev, ...syncQueue]);
    }
  };

  const addToSyncQueue = (operation: () => Promise<void>) => {
    setSyncQueue((prev) => [...prev, operation]);
    if (isOnline) {
      processSyncQueue();
    }
  };

  return {
    isOnline,
    lastSyncTime,
    syncQueue,
    addToSyncQueue,
    processSyncQueue,
  };
}; 