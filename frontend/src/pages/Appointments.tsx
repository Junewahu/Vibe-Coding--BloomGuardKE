import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  CalendarMonth,
  AccessTime,
  Person,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { theme as customTheme } from '../utils/theme';

// Placeholder data - replace with actual API calls
const mockAppointments = [
  {
    id: 1,
    patientName: 'John Doe',
    date: '2024-03-01',
    time: '09:00 AM',
    type: 'checkup',
    status: 'scheduled',
    doctor: 'Dr. Smith',
    notes: 'Regular checkup',
  },
  {
    id: 2,
    patientName: 'Jane Smith',
    date: '2024-03-01',
    time: '10:30 AM',
    type: 'followup',
    status: 'scheduled',
    doctor: 'Dr. Johnson',
    notes: 'Follow-up after vaccination',
  },
  // Add more mock appointments as needed
];

const appointmentTypes = [
  { value: 'checkup', label: 'Regular Checkup' },
  { value: 'followup', label: 'Follow-up' },
  { value: 'vaccination', label: 'Vaccination' },
  { value: 'consultation', label: 'Consultation' },
];

const Appointments: React.FC = () => {
  const { t } = useTranslation();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [appointmentDialogOpen, setAppointmentDialogOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<typeof mockAppointments[0] | null>(null);

  const handleAddAppointment = () => {
    setSelectedAppointment(null);
    setAppointmentDialogOpen(true);
  };

  const handleEditAppointment = (appointment: typeof mockAppointments[0]) => {
    setSelectedAppointment(appointment);
    setAppointmentDialogOpen(true);
  };

  const handleDialogClose = () => {
    setAppointmentDialogOpen(false);
    setSelectedAppointment(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return customTheme.colors.babyBlue;
      case 'completed':
        return customTheme.colors.lavender;
      case 'cancelled':
        return customTheme.colors.candyPink;
      default:
        return customTheme.colors.babyBlue;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            color: customTheme.colors.deepNavy,
            fontFamily: customTheme.typography.fontFamily.secondary,
            fontWeight: customTheme.typography.fontWeight.bold,
          }}
        >
          {t('appointments.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddAppointment}
          sx={{
            backgroundColor: customTheme.colors.babyBlue,
            color: customTheme.colors.deepNavy,
            '&:hover': {
              backgroundColor: customTheme.colors.skyBlue,
            },
            borderRadius: customTheme.borderRadius.md,
          }}
        >
          {t('appointments.addAppointment')}
        </Button>
      </Box>

      {/* Calendar and Appointments Section */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('appointments.calendar')}
            </Typography>
            {/* Add Calendar Component Here */}
            <Box
              sx={{
                height: 400,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: customTheme.colors.babyBlue + '20',
                borderRadius: customTheme.borderRadius.md,
              }}
            >
              <Typography color="text.secondary">
                {t('appointments.calendarPlaceholder')}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 2,
                color: customTheme.colors.deepNavy,
                fontFamily: customTheme.typography.fontFamily.secondary,
              }}
            >
              {t('appointments.todayAppointments')}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {mockAppointments.map((appointment) => (
                <Card
                  key={appointment.id}
                  sx={{
                    borderRadius: customTheme.borderRadius.md,
                    boxShadow: customTheme.shadows.soft,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography
                        variant="subtitle1"
                        sx={{ color: customTheme.colors.deepNavy }}
                      >
                        {appointment.patientName}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleEditAppointment(appointment)}
                          sx={{ color: customTheme.colors.deepNavy }}
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          sx={{ color: customTheme.colors.deepNavy }}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <AccessTime fontSize="small" sx={{ color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {appointment.time}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Person fontSize="small" sx={{ color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {appointment.doctor}
                      </Typography>
                    </Box>
                    <Chip
                      label={t(`appointments.status.${appointment.status}`)}
                      size="small"
                      sx={{
                        backgroundColor: getStatusColor(appointment.status),
                        color: customTheme.colors.deepNavy,
                      }}
                    />
                  </CardContent>
                </Card>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Appointment Dialog */}
      <Dialog
        open={appointmentDialogOpen}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: customTheme.borderRadius.lg,
            boxShadow: customTheme.shadows.medium,
          },
        }}
      >
        <DialogTitle sx={{ color: customTheme.colors.deepNavy }}>
          {selectedAppointment
            ? t('appointments.editAppointment')
            : t('appointments.addAppointment')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label={t('appointments.patientName')}
              fullWidth
              defaultValue={selectedAppointment?.patientName}
            />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label={t('appointments.date')}
                  type="date"
                  fullWidth
                  defaultValue={selectedAppointment?.date}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label={t('appointments.time')}
                  type="time"
                  fullWidth
                  defaultValue={selectedAppointment?.time}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            <FormControl fullWidth>
              <InputLabel>{t('appointments.type')}</InputLabel>
              <Select
                label={t('appointments.type')}
                defaultValue={selectedAppointment?.type || ''}
              >
                {appointmentTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label={t('appointments.notes')}
              multiline
              rows={3}
              fullWidth
              defaultValue={selectedAppointment?.notes}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleDialogClose}
            sx={{ color: customTheme.colors.deepNavy }}
          >
            {t('common.cancel')}
          </Button>
          <Button
            variant="contained"
            sx={{
              backgroundColor: customTheme.colors.babyBlue,
              color: customTheme.colors.deepNavy,
              '&:hover': {
                backgroundColor: customTheme.colors.skyBlue,
              },
            }}
          >
            {selectedAppointment
              ? t('common.save')
              : t('appointments.schedule')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Appointments; 