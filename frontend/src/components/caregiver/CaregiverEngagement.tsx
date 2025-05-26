import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Stack,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  IconButton,
  Tooltip,
  useTheme,
  CircularProgress,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useParams } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { useSnackbar } from 'notistack';

interface Caregiver {
  id: string;
  patient_id: string;
  name: string;
  relationship: string;
  phone: string;
  email?: string;
  address?: string;
  is_primary: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface CaregiverInteraction {
  id: string;
  caregiver_id: string;
  patient_id: string;
  type: 'visit' | 'call' | 'message' | 'other';
  status: 'scheduled' | 'completed' | 'cancelled' | 'missed';
  scheduled_date: string;
  completed_date?: string;
  notes?: string;
  outcome?: string;
  created_at: string;
  updated_at: string;
}

const caregiverSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  relationship: z.string().min(1, 'Relationship is required'),
  phone: z.string().min(1, 'Phone number is required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  address: z.string().optional(),
  is_primary: z.boolean().default(false),
  notes: z.string().optional(),
});

const interactionSchema = z.object({
  type: z.enum(['visit', 'call', 'message', 'other']),
  scheduled_date: z.string().min(1, 'Scheduled date is required'),
  notes: z.string().optional(),
});

export const CaregiverEngagement: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const [loading, setLoading] = useState(true);
  const [caregivers, setCaregivers] = useState<Caregiver[]>([]);
  const [interactions, setInteractions] = useState<CaregiverInteraction[]>([]);
  const [stats, setStats] = useState({
    totalInteractions: 0,
    completedInteractions: 0,
    upcomingInteractions: 0,
    interactionTrend: 0,
  });
  const [isCaregiverModalOpen, setIsCaregiverModalOpen] = useState(false);
  const [isInteractionModalOpen, setIsInteractionModalOpen] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const theme = useTheme();

  const { register: registerCaregiver, handleSubmit: handleSubmitCaregiver, reset: resetCaregiver, formState: { errors: caregiverErrors } } = useForm({
    resolver: zodResolver(caregiverSchema),
  });

  const { register: registerInteraction, handleSubmit: handleSubmitInteraction, reset: resetInteraction, formState: { errors: interactionErrors } } = useForm({
    resolver: zodResolver(interactionSchema),
  });

  useEffect(() => {
    if (patientId) {
      loadCaregiversAndInteractions();
    }
  }, [patientId]);

  const loadCaregiversAndInteractions = async () => {
    try {
      setLoading(true);
      // TODO: Implement API calls to fetch caregivers and interactions
      // For now, using mock data
      const mockCaregivers: Caregiver[] = [
        {
          id: '1',
          patient_id: patientId!,
          name: 'John Doe',
          relationship: 'Spouse',
          phone: '+254712345678',
          is_primary: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      const mockInteractions: CaregiverInteraction[] = [
        {
          id: '1',
          caregiver_id: '1',
          patient_id: patientId!,
          type: 'visit',
          status: 'completed',
          scheduled_date: new Date().toISOString(),
          completed_date: new Date().toISOString(),
          notes: 'Regular check-up visit',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      setCaregivers(mockCaregivers);
      setInteractions(mockInteractions);
      calculateStats(mockInteractions);
    } catch (error) {
      enqueueSnackbar('Failed to load caregivers and interactions', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (interactions: CaregiverInteraction[]) => {
    const now = new Date();
    const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
    
    const total = interactions.length;
    const completed = interactions.filter(i => i.status === 'completed').length;
    const upcoming = interactions.filter(i => 
      i.status === 'scheduled' && new Date(i.scheduled_date) > now
    ).length;

    const thisMonth = interactions.filter(i => new Date(i.created_at) >= lastMonth).length;
    const lastMonthCount = interactions.filter(i => 
      new Date(i.created_at) >= new Date(lastMonth.getFullYear(), lastMonth.getMonth() - 1, lastMonth.getDate()) &&
      new Date(i.created_at) < lastMonth
    ).length;

    const trend = lastMonthCount === 0 ? 0 : ((thisMonth - lastMonthCount) / lastMonthCount) * 100;

    setStats({
      totalInteractions: total,
      completedInteractions: completed,
      upcomingInteractions: upcoming,
      interactionTrend: trend,
    });
  };

  const onSubmitCaregiver = async (data: any) => {
    try {
      // TODO: Implement API call to create caregiver
      const newCaregiver: Caregiver = {
        id: Date.now().toString(),
        patient_id: patientId!,
        ...data,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setCaregivers([...caregivers, newCaregiver]);
      setIsCaregiverModalOpen(false);
      resetCaregiver();
      enqueueSnackbar('Caregiver added successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to add caregiver', { variant: 'error' });
    }
  };

  const onSubmitInteraction = async (data: any) => {
    try {
      // TODO: Implement API call to create interaction
      const newInteraction: CaregiverInteraction = {
        id: Date.now().toString(),
        caregiver_id: caregivers[0].id, // For now, using first caregiver
        patient_id: patientId!,
        ...data,
        status: 'scheduled',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setInteractions([...interactions, newInteraction]);
      setIsInteractionModalOpen(false);
      resetInteraction();
      calculateStats([...interactions, newInteraction]);
      enqueueSnackbar('Interaction scheduled successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to schedule interaction', { variant: 'error' });
    }
  };

  const updateInteractionStatus = async (interactionId: string, newStatus: CaregiverInteraction['status']) => {
    try {
      // TODO: Implement API call to update interaction status
      const updatedInteractions = interactions.map(i => 
        i.id === interactionId 
          ? { 
              ...i, 
              status: newStatus,
              completed_date: newStatus === 'completed' ? new Date().toISOString() : i.completed_date,
              updated_at: new Date().toISOString(),
            }
          : i
      );

      setInteractions(updatedInteractions);
      calculateStats(updatedInteractions);
      enqueueSnackbar('Interaction status updated successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to update interaction status', { variant: 'error' });
    }
  };

  if (loading) {
    return (
      <Box p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Stack spacing={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4">Caregiver Engagement</Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              onClick={() => setIsCaregiverModalOpen(true)}
            >
              Add Caregiver
            </Button>
            <Button
              variant="contained"
              onClick={() => setIsInteractionModalOpen(true)}
            >
              Schedule Interaction
            </Button>
          </Stack>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Interactions
              </Typography>
              <Typography variant="h4">
                {stats.totalInteractions}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.interactionTrend > 0 ? '+' : ''}{stats.interactionTrend.toFixed(1)}% from last month
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Completed
              </Typography>
              <Typography variant="h4">
                {stats.completedInteractions}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Upcoming
              </Typography>
              <Typography variant="h4">
                {stats.upcomingInteractions}
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Caregivers
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Relationship</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {caregivers.map((caregiver) => (
                  <TableRow key={caregiver.id}>
                    <TableCell>{caregiver.name}</TableCell>
                    <TableCell>{caregiver.relationship}</TableCell>
                    <TableCell>
                      {caregiver.phone}
                      {caregiver.email && <br />}
                      {caregiver.email}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caregiver.is_primary ? 'Primary' : 'Secondary'}
                        color={caregiver.is_primary ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <Tooltip title="Edit">
                          <span>Edit</span>
                        </Tooltip>
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Caregiver Modal */}
        <Dialog
          open={isCaregiverModalOpen}
          onClose={() => setIsCaregiverModalOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add Caregiver</DialogTitle>
          <DialogContent>
            <form onSubmit={handleSubmitCaregiver(onSubmitCaregiver)}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Name</InputLabel>
                  <TextField
                    {...registerCaregiver('name')}
                    label="Name"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Relationship</InputLabel>
                  <TextField
                    {...registerCaregiver('relationship')}
                    label="Relationship"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Phone</InputLabel>
                  <TextField
                    {...registerCaregiver('phone')}
                    label="Phone"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Email (Optional)</InputLabel>
                  <TextField
                    {...registerCaregiver('email')}
                    label="Email (Optional)"
                    type="email"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Address (Optional)</InputLabel>
                  <TextField
                    {...registerCaregiver('address')}
                    label="Address (Optional)"
                    multiline
                    rows={3}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Notes (Optional)</InputLabel>
                  <TextField
                    {...registerCaregiver('notes')}
                    label="Notes (Optional)"
                    multiline
                    rows={4}
                  />
                </FormControl>
              </Stack>
            </form>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsCaregiverModalOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleSubmitCaregiver(onSubmitCaregiver)}
            >
              Add Caregiver
            </Button>
          </DialogActions>
        </Dialog>

        {/* Interaction Modal */}
        <Dialog
          open={isInteractionModalOpen}
          onClose={() => setIsInteractionModalOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Schedule Interaction</DialogTitle>
          <DialogContent>
            <form onSubmit={handleSubmitInteraction(onSubmitInteraction)}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    {...registerInteraction('type')}
                    label="Type"
                  >
                    <MenuItem value="visit">Visit</MenuItem>
                    <MenuItem value="call">Call</MenuItem>
                    <MenuItem value="message">Message</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Scheduled Date</InputLabel>
                  <TextField
                    {...registerInteraction('scheduled_date')}
                    type="datetime-local"
                    label="Scheduled Date"
                    InputLabelProps={{
                      shrink: true,
                    }}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Notes (Optional)</InputLabel>
                  <TextField
                    {...registerInteraction('notes')}
                    label="Notes (Optional)"
                    multiline
                    rows={4}
                  />
                </FormControl>
              </Stack>
            </form>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsInteractionModalOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleSubmitInteraction(onSubmitInteraction)}
            >
              Schedule
            </Button>
          </DialogActions>
        </Dialog>
      </Stack>
    </Box>
  );
};

export default CaregiverEngagement; 