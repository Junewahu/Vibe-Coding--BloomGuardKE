import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Button,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  LocationOn,
  Sync,
  CheckCircle,
  Warning,
  NavigateNext,
  OfflineBolt,
} from '@mui/icons-material';
import { theme } from '../../theme';
import { useOfflineSync } from '../../hooks/useOfflineSync';
import { useGeolocation } from '../../hooks/useGeolocation';

interface Task {
  id: string;
  patientName: string;
  address: string;
  type: 'visit' | 'follow-up' | 'education';
  status: 'pending' | 'in-progress' | 'completed';
  scheduledDate: string;
  notes?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

interface CHWFieldAppProps {
  tasks: Task[];
  onTaskUpdate: (taskId: string, status: Task['status'], notes?: string) => void;
  onSync: () => Promise<void>;
}

export const CHWFieldApp: React.FC<CHWFieldAppProps> = ({
  tasks,
  onTaskUpdate,
  onSync,
}) => {
  const { t } = useTranslation();
  const { isOnline, lastSyncTime, syncQueue } = useOfflineSync();
  const { location, error: locationError } = useGeolocation();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const handleTaskSelect = (task: Task) => {
    setSelectedTask(task);
  };

  const handleTaskComplete = async (taskId: string) => {
    if (!location) {
      // Show error about missing location
      return;
    }

    await onTaskUpdate(taskId, 'completed', 'Visit completed with location data');
  };

  const getTaskStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in-progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 2 }}>
      {/* Sync Status */}
      <Card sx={{ p: 2, mb: 2, bgcolor: theme.palette.background.paper }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip
            icon={isOnline ? <Sync /> : <OfflineBolt />}
            label={isOnline ? t('chw.online') : t('chw.offline')}
            color={isOnline ? 'success' : 'warning'}
          />
          <Typography variant="body2" color="text.secondary">
            {t('chw.lastSync')}: {lastSyncTime}
          </Typography>
          {syncQueue.length > 0 && (
            <Chip
              label={`${syncQueue.length} ${t('chw.pendingSync')}`}
              color="warning"
            />
          )}
          <Button
            variant="outlined"
            startIcon={<Sync />}
            onClick={onSync}
            disabled={!isOnline}
          >
            {t('common.sync')}
          </Button>
        </Stack>
      </Card>

      {/* Task List */}
      <List>
        {tasks.map((task) => (
          <Card
            key={task.id}
            sx={{
              mb: 2,
              p: 2,
              bgcolor: theme.palette.background.paper,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: theme.palette.action.hover,
              },
            }}
            onClick={() => handleTaskSelect(task)}
          >
            <ListItem
              secondaryAction={
                <IconButton edge="end">
                  <NavigateNext />
                </IconButton>
              }
            >
              <ListItemIcon>
                <LocationOn color="primary" />
              </ListItemIcon>
              <ListItemText
                primary={task.patientName}
                secondary={
                  <Stack spacing={1}>
                    <Typography variant="body2" color="text.secondary">
                      {task.address}
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <Chip
                        size="small"
                        label={t(`chw.taskType.${task.type}`)}
                        color="primary"
                      />
                      <Chip
                        size="small"
                        label={t(`chw.status.${task.status}`)}
                        color={getTaskStatusColor(task.status)}
                      />
                    </Stack>
                  </Stack>
                }
              />
            </ListItem>
          </Card>
        ))}
      </List>

      {/* Task Details Modal */}
      {selectedTask && (
        <Card sx={{ p: 2, mt: 2, bgcolor: theme.palette.background.paper }}>
          <Typography variant="h6" gutterBottom>
            {selectedTask.patientName}
          </Typography>
          <Stack spacing={2}>
            <Typography variant="body2">
              {t('chw.address')}: {selectedTask.address}
            </Typography>
            <Typography variant="body2">
              {t('chw.scheduledDate')}: {selectedTask.scheduledDate}
            </Typography>
            {selectedTask.notes && (
              <Typography variant="body2">{selectedTask.notes}</Typography>
            )}
            <Button
              variant="contained"
              startIcon={<CheckCircle />}
              onClick={() => handleTaskComplete(selectedTask.id)}
              disabled={!location}
            >
              {t('chw.markComplete')}
            </Button>
          </Stack>
        </Card>
      )}

      {/* Location Error */}
      {locationError && (
        <Card sx={{ p: 2, mt: 2, bgcolor: theme.palette.error.light }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Warning color="error" />
            <Typography color="error">
              {t('chw.locationError')}
            </Typography>
          </Stack>
        </Card>
      )}
    </Box>
  );
}; 