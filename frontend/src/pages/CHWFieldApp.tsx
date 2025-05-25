import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Button,
  useTheme,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Sync as SyncIcon,
  Map as MapIcon,
  DirectionsWalk as WalkIcon,
  Phone as PhoneIcon,
  WhatsApp as WhatsAppIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomLayout from '@components/layout/BloomLayout';
import BloomCard from '@components/common/BloomCard';

interface Task {
  id: string;
  title: string;
  address: string;
  type: 'visit' | 'followup' | 'emergency';
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
  coordinates: {
    lat: number;
    lng: number;
  };
  patient: {
    name: string;
    age: number;
    phone: string;
  };
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Vaccination Follow-up',
    address: '123 Main St, Nairobi',
    type: 'followup',
    status: 'pending',
    priority: 'high',
    coordinates: {
      lat: -1.2921,
      lng: 36.8219,
    },
    patient: {
      name: 'John Doe',
      age: 2,
      phone: '+254 712 345 678',
    },
  },
  {
    id: '2',
    title: 'Regular Check-up',
    address: '456 Park Ave, Nairobi',
    type: 'visit',
    status: 'in-progress',
    priority: 'medium',
    coordinates: {
      lat: -1.2921,
      lng: 36.8219,
    },
    patient: {
      name: 'Jane Smith',
      age: 1,
      phone: '+254 712 345 679',
    },
  },
];

const CHWFieldApp: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [tasks] = useState<Task[]>(mockTasks);
  const [isOnline, setIsOnline] = useState(true);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return theme.palette.status.error;
      case 'medium':
        return theme.palette.status.warning;
      case 'low':
        return theme.palette.status.success;
      default:
        return theme.palette.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: theme.palette.status.success }} />;
      case 'in-progress':
        return <WarningIcon sx={{ color: theme.palette.status.warning }} />;
      default:
        return null;
    }
  };

  return (
    <BloomLayout title={t('Field Tasks')}>
      <Box sx={{ p: 3 }}>
        {/* Status Bar */}
        <BloomCard
          title={t('Field Status')}
          subtitle={isOnline ? t('Online') : t('Offline')}
          status={isOnline ? 'success' : 'error'}
          syncStatus={isOnline ? t('Synced 5m ago') : t('Offline - 3 tasks pending sync')}
        >
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<MapIcon />}
              sx={{ borderRadius: '2rem' }}
            >
              {t('View Map')}
            </Button>
            <Button
              variant="outlined"
              startIcon={<SyncIcon />}
              sx={{ borderRadius: '2rem' }}
            >
              {t('Sync Now')}
            </Button>
          </Box>
        </BloomCard>

        {/* Task List */}
        <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
          {t('Today\'s Tasks')}
        </Typography>
        <List>
          {tasks.map((task) => (
            <BloomCard key={task.id} sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Box>
                  <Typography variant="subtitle1">{task.title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {task.patient.name} • {task.patient.age} {t('years old')}
                  </Typography>
                </Box>
                <Chip
                  label={t(task.priority)}
                  size="small"
                  sx={{
                    backgroundColor: getPriorityColor(task.priority),
                    color: theme.palette.common.white,
                  }}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <LocationIcon sx={{ mr: 1, color: theme.palette.text.secondary }} />
                <Typography variant="body2">{task.address}</Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton size="small">
                    <PhoneIcon />
                  </IconButton>
                  <IconButton size="small">
                    <WhatsAppIcon />
                  </IconButton>
                  <IconButton size="small">
                    <WalkIcon />
                  </IconButton>
                </Box>
                <Button
                  variant="contained"
                  size="small"
                  sx={{ borderRadius: '1rem' }}
                >
                  {t('Start Visit')}
                </Button>
              </Box>
            </BloomCard>
          ))}
        </List>
      </Box>
    </BloomLayout>
  );
};

export default CHWFieldApp; 