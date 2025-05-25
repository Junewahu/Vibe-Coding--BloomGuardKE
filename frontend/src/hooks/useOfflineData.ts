import { useState, useEffect, useCallback } from 'react';
import { syncService } from '../services/syncService';

interface UseOfflineDataOptions<T> {
  key: string;
  initialData?: T;
  syncOnOnline?: boolean;
  validateData?: (data: T) => boolean;
}

export function useOfflineData<T>({
  key,
  initialData,
  syncOnOnline = true,
  validateData
}: UseOfflineDataOptions<T>) {
  const [data, setData] = useState<T | null>(initialData || null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const offlineData = await syncService.getOfflineData(key);
      if (offlineData) {
        if (!validateData || validateData(offlineData)) {
          setData(offlineData);
        } else {
          throw new Error('Invalid offline data');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load offline data'));
    } finally {
      setIsLoading(false);
    }
  }, [key, validateData]);

  const saveData = useCallback(async (newData: T) => {
    try {
      setError(null);
      await syncService.saveOfflineData(key, newData);
      setData(newData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to save offline data'));
    }
  }, [key]);

  const clearData = useCallback(async () => {
    try {
      setError(null);
      await syncService.clearOfflineData(key);
      setData(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to clear offline data'));
    }
  }, [key]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (syncOnOnline) {
      const handleOnline = () => {
        loadData();
      };

      window.addEventListener('online', handleOnline);
      return () => window.removeEventListener('online', handleOnline);
    }
  }, [syncOnOnline, loadData]);

  return {
    data,
    isLoading,
    error,
    saveData,
    clearData,
    refresh: loadData
  };
} 