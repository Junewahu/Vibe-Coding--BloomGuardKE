import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  useTheme
} from '@mui/material';
import { syncService } from '../services/syncService';
import { useOfflineData } from '../hooks/useOfflineData';

interface OfflineFormProps<T> {
  formKey: string;
  onSubmit: (data: T) => Promise<void>;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  children: (props: {
    submitForm: (data: T) => Promise<void>;
    isSubmitting: boolean;
    error: Error | null;
  }) => React.ReactNode;
}

export function OfflineForm<T>({
  formKey,
  onSubmit,
  onSuccess,
  onError,
  children
}: OfflineFormProps<T>) {
  const { t } = useTranslation();
  const theme = useTheme();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const { data: pendingSubmissions, saveData, clearData } = useOfflineData<T[]>({
    key: `form_${formKey}_pending`,
    initialData: []
  });

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const processPendingSubmissions = async () => {
    if (!pendingSubmissions?.length) return;

    for (const submission of pendingSubmissions) {
      try {
        await onSubmit(submission);
      } catch (err) {
        console.error('Failed to process pending submission:', err);
        // Keep the failed submission in the queue
        continue;
      }
    }

    // Clear all successfully processed submissions
    await clearData();
  };

  useEffect(() => {
    if (isOnline && pendingSubmissions?.length) {
      processPendingSubmissions();
    }
  }, [isOnline, pendingSubmissions]);

  const submitForm = async (data: T) => {
    setIsSubmitting(true);
    setError(null);

    try {
      if (isOnline) {
        await onSubmit(data);
        onSuccess?.();
      } else {
        // Store submission for later
        const submissions = pendingSubmissions || [];
        await saveData([...submissions, data]);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Form submission failed');
      setError(error);
      onError?.(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box>
      {!isOnline && (
        <Alert 
          severity="warning" 
          sx={{ mb: 2 }}
        >
          {t('form.offlineWarning')}
          {pendingSubmissions?.length ? (
            <Typography variant="body2" sx={{ mt: 1 }}>
              {t('form.pendingSubmissions', { count: pendingSubmissions.length })}
            </Typography>
          ) : null}
        </Alert>
      )}

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error.message}
        </Alert>
      )}

      {children({
        submitForm,
        isSubmitting,
        error
      })}

      {isSubmitting && (
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mt: 2
          }}
        >
          <CircularProgress size={24} />
          <Typography 
            variant="body2" 
            sx={{ ml: 1, color: theme.palette.text.secondary }}
          >
            {isOnline ? t('form.submitting') : t('form.savingOffline')}
          </Typography>
        </Box>
      )}
    </Box>
  );
} 