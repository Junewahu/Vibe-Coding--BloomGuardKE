import React, { useEffect, useState } from 'react';
import { Chip, Tooltip } from '@mui/material';
import { CloudSync, CloudOff, CloudDone } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { theme as customTheme } from '../utils/theme';
import { syncService } from '../services/syncService';

const SyncStatus: React.FC = () => {
  const { t } = useTranslation();
  const [status, setStatus] = useState<{
    isOnline: boolean;
    pendingCount: number;
    lastSync: Date | null;
    syncInProgress: boolean;
  }>({
    isOnline: navigator.onLine,
    pendingCount: 0,
    lastSync: null,
    syncInProgress: false,
  });

  useEffect(() => {
    const updateStatus = async () => {
      const syncStatus = await syncService.getSyncStatus();
      setStatus(syncStatus);
    };

    const handleOnline = () => {
      setStatus(prev => ({ ...prev, isOnline: true }));
      syncService.triggerSync();
    };

    const handleOffline = () => {
      setStatus(prev => ({ ...prev, isOnline: false }));
    };

    // Initial status check
    updateStatus();

    // Set up event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Set up periodic status updates
    const interval = setInterval(updateStatus, 5000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  const getStatusColor = () => {
    if (!status.isOnline) return customTheme.colors.error;
    if (status.syncInProgress) return customTheme.colors.warning;
    if (status.pendingCount > 0) return customTheme.colors.warning;
    return customTheme.colors.success;
  };

  const getStatusIcon = () => {
    if (!status.isOnline) return <CloudOff />;
    if (status.syncInProgress) return <CloudSync />;
    if (status.pendingCount > 0) return <CloudSync />;
    return <CloudDone />;
  };

  const getStatusText = () => {
    if (!status.isOnline) return t('common.offline');
    if (status.syncInProgress) return t('common.sync');
    if (status.pendingCount > 0) return `${status.pendingCount} ${t('common.pending')}`;
    return status.lastSync
      ? `${t('common.synced')} ${new Date(status.lastSync).toLocaleTimeString()}`
      : t('common.synced');
  };

  const getTooltipText = () => {
    if (!status.isOnline) return t('errors.offline');
    if (status.syncInProgress) return t('common.syncing');
    if (status.pendingCount > 0) return `${status.pendingCount} ${t('common.pendingChanges')}`;
    return status.lastSync
      ? `${t('common.lastSync')}: ${new Date(status.lastSync).toLocaleString()}`
      : t('common.noSyncHistory');
  };

  return (
    <Tooltip title={getTooltipText()}>
      <Chip
        icon={getStatusIcon()}
        label={getStatusText()}
        sx={{
          backgroundColor: getStatusColor(),
          color: customTheme.colors.white,
          '& .MuiChip-icon': {
            color: customTheme.colors.white,
          },
          transition: `all ${customTheme.transitions.normal} ${customTheme.transitions.easeInOut}`,
        }}
      />
    </Tooltip>
  );
};

export default SyncStatus; 