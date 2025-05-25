import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Avatar,
  Button,
  Chip,
  Divider,
  useTheme,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  Vaccines as VaccinesIcon,
  EventNote as EventNoteIcon,
  Person as PersonIcon,
  QrCode as QrCodeIcon,
  Phone as PhoneIcon,
  WhatsApp as WhatsAppIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import BloomCard from '@components/common/BloomCard';
import BloomLayout from '@components/layout/BloomLayout';

interface TimelineEvent {
  id: string;
  type: 'vaccination' | 'milestone' | 'visit' | 'note';
  title: string;
  date: string;
  description: string;
  status: 'completed' | 'upcoming' | 'missed';
}

interface Caregiver {
  id: string;
  name: string;
  relationship: string;
  phone: string;
  whatsapp: string;
}

const mockTimelineEvents: TimelineEvent[] = [
  {
    id: '1',
    type: 'vaccination',
    title: 'BCG Vaccination',
    date: '2024-01-15',
    description: 'Completed successfully',
    status: 'completed',
  },
  {
    id: '2',
    type: 'milestone',
    title: 'First Steps',
    date: '2024-02-01',
    description: 'Started walking independently',
    status: 'completed',
  },
  {
    id: '3',
    type: 'visit',
    title: 'Regular Check-up',
    date: '2024-02-20',
    description: 'Scheduled appointment',
    status: 'upcoming',
  },
];

const mockCaregivers: Caregiver[] = [
  {
    id: '1',
    name: 'Mary Doe',
    relationship: 'Mother',
    phone: '+254 712 345 678',
    whatsapp: '+254 712 345 678',
  },
];

const PatientProfile: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [events] = useState<TimelineEvent[]>(mockTimelineEvents);
  const [caregivers] = useState<Caregiver[]>(mockCaregivers);

  const getEventColor = (type: string) => {
    switch (type) {
      case 'vaccination':
        return theme.palette.primary.main;
      case 'milestone':
        return theme.palette.secondary.main;
      case 'visit':
        return theme.palette.accent.main;
      case 'note':
        return theme.palette.grey[500];
      default:
        return theme.palette.grey[500];
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'vaccination':
        return <VaccinesIcon />;
      case 'milestone':
        return <EventNoteIcon />;
      case 'visit':
        return <PersonIcon />;
      case 'note':
        return <EventNoteIcon />;
      default:
        return null;
    }
  };

  return (
    <BloomLayout title={t('Patient Profile')}>
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Patient Info Card */}
          <Grid item xs={12} md={4}>
            <BloomCard>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    mb: 2,
                    backgroundColor: theme.palette.primary.main,
                  }}
                >
                  <PersonIcon sx={{ fontSize: 60 }} />
                </Avatar>
                <Typography variant="h5" gutterBottom>
                  John Doe
                </Typography>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  2 years old
                </Typography>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<QrCodeIcon />}
                    sx={{ borderRadius: '2rem' }}
                  >
                    {t('View QR')}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<QrCodeIcon />}
                    sx={{ borderRadius: '2rem' }}
                  >
                    {t('Download')}
                  </Button>
                </Box>
              </Box>
            </BloomCard>

            {/* Caregiver Info */}
            <BloomCard title={t('Caregivers')} sx={{ mt: 3 }}>
              {caregivers.map((caregiver) => (
                <Box key={caregiver.id} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">{caregiver.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {caregiver.relationship}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Button
                      size="small"
                      startIcon={<PhoneIcon />}
                      sx={{ borderRadius: '1rem' }}
                    >
                      {t('Call')}
                    </Button>
                    <Button
                      size="small"
                      startIcon={<WhatsAppIcon />}
                      sx={{ borderRadius: '1rem' }}
                    >
                      {t('WhatsApp')}
                    </Button>
                  </Box>
                </Box>
              ))}
            </BloomCard>
          </Grid>

          {/* Timeline */}
          <Grid item xs={12} md={8}>
            <BloomCard title={t('Patient Timeline')}>
              <Timeline>
                {events.map((event, index) => (
                  <TimelineItem key={event.id}>
                    <TimelineSeparator>
                      <TimelineDot
                        sx={{
                          backgroundColor: getEventColor(event.type),
                          color: theme.palette.common.white,
                        }}
                      >
                        {getEventIcon(event.type)}
                      </TimelineDot>
                      {index < events.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle1">{event.title}</Typography>
                          <Chip
                            label={t(event.status)}
                            size="small"
                            sx={{
                              backgroundColor:
                                event.status === 'completed'
                                  ? theme.palette.status.success
                                  : event.status === 'missed'
                                  ? theme.palette.status.error
                                  : theme.palette.status.warning,
                              color: theme.palette.common.white,
                            }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(event.date).toLocaleDateString()}
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                          {event.description}
                        </Typography>
                      </Box>
                      {index < events.length - 1 && <Divider />}
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            </BloomCard>
          </Grid>
        </Grid>
      </Box>
    </BloomLayout>
  );
};

export default PatientProfile; 