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
  LinearProgress,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useParams } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { useSnackbar } from 'notistack';

interface AdherenceMetric {
  id: string;
  patient_id: string;
  type: 'medication' | 'appointment' | 'lifestyle' | 'other';
  target: number;
  achieved: number;
  period: 'daily' | 'weekly' | 'monthly';
  start_date: string;
  end_date?: string;
  status: 'active' | 'completed' | 'cancelled';
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface Incentive {
  id: string;
  patient_id: string;
  type: 'monetary' | 'non_monetary' | 'recognition';
  value: string;
  description: string;
  criteria: {
    metric_type: AdherenceMetric['type'];
    target_value: number;
    period: AdherenceMetric['period'];
  };
  status: 'pending' | 'earned' | 'redeemed' | 'expired';
  earned_at?: string;
  redeemed_at?: string;
  expiry_date?: string;
  created_at: string;
  updated_at: string;
}

const adherenceSchema = z.object({
  type: z.enum(['medication', 'appointment', 'lifestyle', 'other']),
  target: z.number().min(1, 'Target must be at least 1'),
  period: z.enum(['daily', 'weekly', 'monthly']),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  notes: z.string().optional(),
});

const incentiveSchema = z.object({
  type: z.enum(['monetary', 'non_monetary', 'recognition']),
  value: z.string().min(1, 'Value is required'),
  description: z.string().min(1, 'Description is required'),
  criteria: z.object({
    metric_type: z.enum(['medication', 'appointment', 'lifestyle', 'other']),
    target_value: z.number().min(1, 'Target value must be at least 1'),
    period: z.enum(['daily', 'weekly', 'monthly']),
  }),
  expiry_date: z.string().optional(),
});

export const IncentivesAdherence: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<AdherenceMetric[]>([]);
  const [incentives, setIncentives] = useState<Incentive[]>([]);
  const [stats, setStats] = useState({
    overallAdherence: 0,
    activeMetrics: 0,
    earnedIncentives: 0,
    adherenceTrend: 0,
  });
  const [isMetricModalOpen, setIsMetricModalOpen] = useState(false);
  const [isIncentiveModalOpen, setIsIncentiveModalOpen] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const theme = useTheme();

  const { register: registerMetric, handleSubmit: handleSubmitMetric, reset: resetMetric, formState: { errors: metricErrors } } = useForm({
    resolver: zodResolver(adherenceSchema),
  });

  const { register: registerIncentive, handleSubmit: handleSubmitIncentive, reset: resetIncentive, formState: { errors: incentiveErrors } } = useForm({
    resolver: zodResolver(incentiveSchema),
  });

  useEffect(() => {
    if (patientId) {
      loadMetricsAndIncentives();
    }
  }, [patientId]);

  const loadMetricsAndIncentives = async () => {
    try {
      setLoading(true);
      // TODO: Implement API calls to fetch metrics and incentives
      // For now, using mock data
      const mockMetrics: AdherenceMetric[] = [
        {
          id: '1',
          patient_id: patientId!,
          type: 'medication',
          target: 30,
          achieved: 28,
          period: 'monthly',
          start_date: new Date().toISOString(),
          status: 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      const mockIncentives: Incentive[] = [
        {
          id: '1',
          patient_id: patientId!,
          type: 'monetary',
          value: 'KES 500',
          description: 'Monthly adherence bonus',
          criteria: {
            metric_type: 'medication',
            target_value: 28,
            period: 'monthly',
          },
          status: 'earned',
          earned_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      setMetrics(mockMetrics);
      setIncentives(mockIncentives);
      calculateStats(mockMetrics, mockIncentives);
    } catch (error) {
      enqueueSnackbar('Failed to load adherence metrics and incentives', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (metrics: AdherenceMetric[], incentives: Incentive[]) => {
    const activeMetrics = metrics.filter(m => m.status === 'active');
    const overallAdherence = activeMetrics.length > 0
      ? activeMetrics.reduce((acc, m) => acc + (m.achieved / m.target), 0) / activeMetrics.length * 100
      : 0;
    const earnedIncentives = incentives.filter(i => i.status === 'earned').length;

    // Calculate trend (comparing current month to previous month)
    const now = new Date();
    const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
    const thisMonthMetrics = metrics.filter(m => new Date(m.created_at) >= lastMonth);
    const lastMonthMetrics = metrics.filter(m => 
      new Date(m.created_at) >= new Date(lastMonth.getFullYear(), lastMonth.getMonth() - 1, lastMonth.getDate()) &&
      new Date(m.created_at) < lastMonth
    );

    const thisMonthAdherence = thisMonthMetrics.length > 0
      ? thisMonthMetrics.reduce((acc, m) => acc + (m.achieved / m.target), 0) / thisMonthMetrics.length * 100
      : 0;
    const lastMonthAdherence = lastMonthMetrics.length > 0
      ? lastMonthMetrics.reduce((acc, m) => acc + (m.achieved / m.target), 0) / lastMonthMetrics.length * 100
      : 0;

    const trend = lastMonthAdherence === 0 ? 0 : ((thisMonthAdherence - lastMonthAdherence) / lastMonthAdherence) * 100;

    setStats({
      overallAdherence,
      activeMetrics: activeMetrics.length,
      earnedIncentives,
      adherenceTrend: trend,
    });
  };

  const onSubmitMetric = async (data: any) => {
    try {
      // TODO: Implement API call to create metric
      const newMetric: AdherenceMetric = {
        id: Date.now().toString(),
        patient_id: patientId!,
        ...data,
        achieved: 0,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setMetrics([...metrics, newMetric]);
      setIsMetricModalOpen(false);
      resetMetric();
      calculateStats([...metrics, newMetric], incentives);
      enqueueSnackbar('Adherence metric added successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to add adherence metric', { variant: 'error' });
    }
  };

  const onSubmitIncentive = async (data: any) => {
    try {
      // TODO: Implement API call to create incentive
      const newIncentive: Incentive = {
        id: Date.now().toString(),
        patient_id: patientId!,
        ...data,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setIncentives([...incentives, newIncentive]);
      setIsIncentiveModalOpen(false);
      resetIncentive();
      calculateStats(metrics, [...incentives, newIncentive]);
      enqueueSnackbar('Incentive added successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to add incentive', { variant: 'error' });
    }
  };

  const updateMetricProgress = async (metricId: string, newAchieved: number) => {
    try {
      // TODO: Implement API call to update metric progress
      const updatedMetrics = metrics.map(m => 
        m.id === metricId 
          ? { 
              ...m, 
              achieved: newAchieved,
              status: newAchieved >= m.target ? 'completed' : m.status,
              updated_at: new Date().toISOString(),
            }
          : m
      );

      setMetrics(updatedMetrics);
      calculateStats(updatedMetrics, incentives);
      enqueueSnackbar('Metric progress updated successfully', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Failed to update metric progress', { variant: 'error' });
    }
  };

  if (loading) {
    return (
      <Box p={4}>
        {/* Add loading component */}
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Stack spacing={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4">Incentives & Adherence</Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              onClick={() => setIsMetricModalOpen(true)}
            >
              Add Metric
            </Button>
            <Button
              variant="contained"
              onClick={() => setIsIncentiveModalOpen(true)}
            >
              Add Incentive
            </Button>
          </Stack>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Overall Adherence
              </Typography>
              <Typography variant="h4">
                {stats.overallAdherence.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.adherenceTrend > 0 ? '+' : ''}{stats.adherenceTrend.toFixed(1)}% from last month
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Active Metrics
              </Typography>
              <Typography variant="h4">
                {stats.activeMetrics}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Earned Incentives
              </Typography>
              <Typography variant="h4">
                {stats.earnedIncentives}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Available Incentives
              </Typography>
              <Typography variant="h4">
                {incentives.filter(i => i.status === 'pending').length}
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Adherence Metrics
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Target</TableCell>
                  <TableCell>Achieved</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {metrics.map((metric) => (
                  <TableRow key={metric.id}>
                    <TableCell>{metric.type}</TableCell>
                    <TableCell>{metric.target}</TableCell>
                    <TableCell>{metric.achieved}</TableCell>
                    <TableCell>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={(metric.achieved / metric.target) * 100}
                          color={metric.achieved >= metric.target ? 'success' : 'primary'}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={metric.status}
                        color={metric.status === 'active' ? 'primary' : 'default'}
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

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Incentives
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Criteria</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Earned/Redeemed</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {incentives.map((incentive) => (
                  <TableRow key={incentive.id}>
                    <TableCell>{incentive.type}</TableCell>
                    <TableCell>{incentive.value}</TableCell>
                    <TableCell>
                      {incentive.criteria.metric_type}: {incentive.criteria.target_value} ({incentive.criteria.period})
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={incentive.status}
                        color={
                          incentive.status === 'earned' ? 'success' :
                          incentive.status === 'redeemed' ? 'primary' :
                          incentive.status === 'expired' ? 'error' : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {incentive.earned_at && new Date(incentive.earned_at).toLocaleDateString()}
                      {incentive.redeemed_at && ` (Redeemed: ${new Date(incentive.redeemed_at).toLocaleDateString()})`}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Metric Modal */}
        <Dialog
          open={isMetricModalOpen}
          onClose={() => setIsMetricModalOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add Adherence Metric</DialogTitle>
          <DialogContent>
            <form onSubmit={handleSubmitMetric(onSubmitMetric)}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    {...registerMetric('type')}
                    label="Type"
                  >
                    <MenuItem value="medication">Medication</MenuItem>
                    <MenuItem value="appointment">Appointment</MenuItem>
                    <MenuItem value="lifestyle">Lifestyle</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Target</InputLabel>
                  <TextField
                    {...registerMetric('target', { valueAsNumber: true })}
                    type="number"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Period</InputLabel>
                  <Select
                    {...registerMetric('period')}
                    label="Period"
                  >
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Start Date</InputLabel>
                  <TextField
                    {...registerMetric('start_date')}
                    type="date"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>End Date (Optional)</InputLabel>
                  <TextField
                    {...registerMetric('end_date')}
                    type="date"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Notes (Optional)</InputLabel>
                  <TextField
                    {...registerMetric('notes')}
                    multiline
                    rows={4}
                  />
                </FormControl>
              </Stack>
            </form>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsMetricModalOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleSubmitMetric(onSubmitMetric)}
            >
              Add Metric
            </Button>
          </DialogActions>
        </Dialog>

        {/* Incentive Modal */}
        <Dialog
          open={isIncentiveModalOpen}
          onClose={() => setIsIncentiveModalOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add Incentive</DialogTitle>
          <DialogContent>
            <form onSubmit={handleSubmitIncentive(onSubmitIncentive)}>
              <Stack spacing={3} sx={{ mt: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    {...registerIncentive('type')}
                    label="Type"
                  >
                    <MenuItem value="monetary">Monetary</MenuItem>
                    <MenuItem value="non_monetary">Non-Monetary</MenuItem>
                    <MenuItem value="recognition">Recognition</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Value</InputLabel>
                  <TextField
                    {...registerIncentive('value')}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Description</InputLabel>
                  <TextField
                    {...registerIncentive('description')}
                    multiline
                    rows={4}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Metric Type</InputLabel>
                  <Select
                    {...registerIncentive('criteria.metric_type')}
                    label="Metric Type"
                  >
                    <MenuItem value="medication">Medication</MenuItem>
                    <MenuItem value="appointment">Appointment</MenuItem>
                    <MenuItem value="lifestyle">Lifestyle</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Target Value</InputLabel>
                  <TextField
                    {...registerIncentive('criteria.target_value', { valueAsNumber: true })}
                    type="number"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Period</InputLabel>
                  <Select
                    {...registerIncentive('criteria.period')}
                    label="Period"
                  >
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Expiry Date (Optional)</InputLabel>
                  <TextField
                    {...registerIncentive('expiry_date')}
                    type="date"
                  />
                </FormControl>
              </Stack>
            </form>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsIncentiveModalOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleSubmitIncentive(onSubmitIncentive)}
            >
              Add Incentive
            </Button>
          </DialogActions>
        </Dialog>
      </Stack>
    </Box>
  );
};

export default IncentivesAdherence; 