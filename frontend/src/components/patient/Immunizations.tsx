import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Stack,
  Text,
  Badge,
  Spinner,
  FormControl,
  FormLabel,
  Input,
  Select,
  Card,
  CardHeader,
  CardContent,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { Immunization } from '../../types/patient';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import CloseIcon from '@mui/icons-material/Close';

const immunizationSchema = z.object({
  vaccine_name: z.string().min(1, 'Vaccine name is required'),
  scheduled_date: z.string().min(1, 'Scheduled date is required'),
  administered_date: z.string().optional(),
  batch_number: z.string().optional(),
  administered_by: z.string().optional(),
  status: z.string().min(1, 'Status is required'),
});

type ImmunizationFormData = z.infer<typeof immunizationSchema>;

export const Immunizations: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [immunizations, setImmunizations] = useState<Immunization[]>([]);
  const { currentPatient, getPatient, getImmunizations, createImmunization } = usePatientStore();
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [toastSeverity, setToastSeverity] = useState<'success' | 'error' | 'warning' | 'info'>( 'success');
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ImmunizationFormData>({
    resolver: zodResolver(immunizationSchema),
  });

  useEffect(() => {
    loadPatientAndImmunizations();
  }, [id]);

  const loadPatientAndImmunizations = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      const immunizations = await getImmunizations(id);
      setImmunizations(immunizations);
    } catch (error) {
      setToastMessage(error instanceof Error ? error.message : 'An error occurred');
      setToastSeverity('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = () => setIsModalOpen(true);
  const handleCloseModal = () => {
    setIsModalOpen(false);
    reset();
  };

  const handleAddImmunization = () => {
    reset();
    handleOpenModal();
  };

  const onSubmit = async (data: ImmunizationFormData) => {
    if (!id) return;
    try {
      await createImmunization(id, data);
      setToastMessage('Immunization record created successfully');
      setToastSeverity('success');
      handleCloseModal();
      loadPatientAndImmunizations();
    } catch (error) {
      setToastMessage(error instanceof Error ? error.message : 'An error occurred');
      setToastSeverity('error');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'green';
      case 'scheduled':
        return 'blue';
      case 'missed':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (!currentPatient) {
    return (
      <Box p={4}>
        <Text>Patient not found</Text>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Stack spacing={4}>
        <Flex justify="space-between" align="center">
          <Heading size="lg">Immunization Records</Heading>
          <Flex gap={2}>
            <Button colorScheme="blue" onClick={handleAddImmunization}>
              Add Immunization
            </Button>
            <Button
              colorScheme="red"
              variant="outline"
              onClick={() => navigate(`/patients/${id}`)}
            >
              Back to Patient
            </Button>
          </Flex>
        </Flex>

        <Card>
          <CardHeader>
            <Heading size="md">
              {currentPatient.first_name} {currentPatient.last_name}
            </Heading>
          </CardHeader>
          <CardContent>
            <Table variant="simple">
              <TableHead>
                <TableRow>
                  <TableCell>Vaccine</TableCell>
                  <TableCell>Scheduled Date</TableCell>
                  <TableCell>Administered Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Batch Number</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {immunizations.map((immunization) => (
                  <TableRow key={immunization.id}>
                    <TableCell>{immunization.vaccine_name}</TableCell>
                    <TableCell>{format(new Date(immunization.scheduled_date), 'PPP')}</TableCell>
                    <TableCell>
                      {immunization.administered_date
                        ? format(new Date(immunization.administered_date), 'PPP')
                        : 'Not administered'}
                    </TableCell>
                    <TableCell>
                      <Badge colorScheme={getStatusColor(immunization.status)}>
                        {immunization.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{immunization.batch_number || 'N/A'}</TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="ghost"
                        onClick={() => {/* TODO: Implement view immunization details */}}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {immunizations.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} textAlign="center">
                      No immunization records found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </Stack>

      <Dialog open={isModalOpen} onClose={handleCloseModal}>
        <DialogTitle>
          Add New Immunization Record
          <IconButton
            aria-label="close"
            onClick={handleCloseModal}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1 }}>
            <FormControl fullWidth margin="normal" error={!!errors.vaccine_name}>
              <FormLabel>Vaccine Name</FormLabel>
              <Input {...register('vaccine_name')} />
              {errors.vaccine_name && <Text color="error.main" fontSize="sm">{errors.vaccine_name.message}</Text>}
            </FormControl>
            <FormControl fullWidth margin="normal" error={!!errors.scheduled_date}>
              <FormLabel>Scheduled Date</FormLabel>
              <Input type="date" {...register('scheduled_date')} />
              {errors.scheduled_date && <Text color="error.main" fontSize="sm">{errors.scheduled_date.message}</Text>}
            </FormControl>
            <FormControl fullWidth margin="normal" error={!!errors.administered_date}>
              <FormLabel>Administered Date (Optional)</FormLabel>
              <Input type="date" {...register('administered_date')} />
              {errors.administered_date && <Text color="error.main" fontSize="sm">{errors.administered_date.message}</Text>}
            </FormControl>
            <FormControl fullWidth margin="normal" error={!!errors.batch_number}>
              <FormLabel>Batch Number (Optional)</FormLabel>
              <Input {...register('batch_number')} />
              {errors.batch_number && <Text color="error.main" fontSize="sm">{errors.batch_number.message}</Text>}
            </FormControl>
            <FormControl fullWidth margin="normal" error={!!errors.administered_by}>
              <FormLabel>Administered By (Optional)</FormLabel>
              <Input {...register('administered_by')} />
              {errors.administered_by && <Text color="error.main" fontSize="sm">{errors.administered_by.message}</Text>}
            </FormControl>
            <FormControl fullWidth margin="normal" error={!!errors.status}>
              <FormLabel>Status</FormLabel>
              <Select native {...register('status')}>
                <option value="">Select Status</option>
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="missed">Missed</option>
              </Select>
              {errors.status && <Text color="error.main" fontSize="sm">{errors.status.message}</Text>}
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModal}>Cancel</Button>
          <Button onClick={handleSubmit(onSubmit)} variant="contained" color="primary">Save Record</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toastMessage} autoHideDuration={6000} onClose={() => setToastMessage(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}>
        <Alert onClose={() => setToastMessage(null)} severity={toastSeverity} sx={{ width: '100%' }}>
          {toastMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}; 