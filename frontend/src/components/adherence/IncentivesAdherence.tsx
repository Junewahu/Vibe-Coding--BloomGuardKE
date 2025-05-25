import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Stack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  useToast,
  Spinner,
  Grid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  Text,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useParams } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';

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

  const { isOpen: isMetricModalOpen, onOpen: onMetricModalOpen, onClose: onMetricModalClose } = useDisclosure();
  const { isOpen: isIncentiveModalOpen, onOpen: onIncentiveModalOpen, onClose: onIncentiveModalClose } = useDisclosure();
  const toast = useToast();

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
      toast({
        title: 'Error',
        description: 'Failed to load adherence metrics and incentives',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      onMetricModalClose();
      resetMetric();
      calculateStats([...metrics, newMetric], incentives);
      toast({
        title: 'Success',
        description: 'Adherence metric added successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add adherence metric',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      onIncentiveModalClose();
      resetIncentive();
      calculateStats(metrics, [...incentives, newIncentive]);
      toast({
        title: 'Success',
        description: 'Incentive added successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add incentive',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      toast({
        title: 'Success',
        description: 'Metric progress updated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update metric progress',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  if (loading) {
    return (
      <Box p={4}>
        <Spinner />
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Stack spacing={6}>
        <Flex justify="space-between" align="center">
          <Heading size="lg">Incentives & Adherence</Heading>
          <Stack direction="row">
            <Button colorScheme="blue" onClick={onMetricModalOpen}>
              Add Metric
            </Button>
            <Button colorScheme="green" onClick={onIncentiveModalOpen}>
              Add Incentive
            </Button>
          </Stack>
        </Flex>

        <Grid templateColumns="repeat(4, 1fr)" gap={4}>
          <Stat>
            <StatLabel>Overall Adherence</StatLabel>
            <StatNumber>{stats.overallAdherence.toFixed(1)}%</StatNumber>
            <StatHelpText>
              <StatArrow type={stats.adherenceTrend >= 0 ? 'increase' : 'decrease'} />
              {Math.abs(stats.adherenceTrend).toFixed(1)}% vs last month
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Active Metrics</StatLabel>
            <StatNumber>{stats.activeMetrics}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Earned Incentives</StatLabel>
            <StatNumber>{stats.earnedIncentives}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Available Incentives</StatLabel>
            <StatNumber>
              {incentives.filter(i => i.status === 'pending').length}
            </StatNumber>
          </Stat>
        </Grid>

        <Card p={4}>
          <Heading size="md" mb={4}>Adherence Metrics</Heading>
          <Table>
            <Thead>
              <Tr>
                <Th>Type</Th>
                <Th>Target</Th>
                <Th>Progress</Th>
                <Th>Period</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {metrics.map(metric => (
                <Tr key={metric.id}>
                  <Td>{metric.type}</Td>
                  <Td>{metric.target}</Td>
                  <Td>
                    <Box>
                      <Progress 
                        value={(metric.achieved / metric.target) * 100} 
                        colorScheme={metric.achieved >= metric.target ? 'green' : 'blue'}
                      />
                      <Text fontSize="sm" mt={1}>
                        {metric.achieved} / {metric.target}
                      </Text>
                    </Box>
                  </Td>
                  <Td>{metric.period}</Td>
                  <Td>
                    <Badge colorScheme={
                      metric.status === 'completed' ? 'green' :
                      metric.status === 'active' ? 'blue' : 'gray'
                    }>
                      {metric.status}
                    </Badge>
                  </Td>
                  <Td>
                    {metric.status === 'active' && (
                      <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={() => updateMetricProgress(metric.id, metric.achieved + 1)}
                      >
                        Update Progress
                      </Button>
                    )}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>

        <Card p={4}>
          <Heading size="md" mb={4}>Incentives</Heading>
          <Table>
            <Thead>
              <Tr>
                <Th>Type</Th>
                <Th>Value</Th>
                <Th>Criteria</Th>
                <Th>Status</Th>
                <Th>Earned/Redeemed</Th>
              </Tr>
            </Thead>
            <Tbody>
              {incentives.map(incentive => (
                <Tr key={incentive.id}>
                  <Td>{incentive.type}</Td>
                  <Td>{incentive.value}</Td>
                  <Td>
                    {incentive.criteria.metric_type}: {incentive.criteria.target_value} ({incentive.criteria.period})
                  </Td>
                  <Td>
                    <Badge colorScheme={
                      incentive.status === 'earned' ? 'green' :
                      incentive.status === 'redeemed' ? 'purple' :
                      incentive.status === 'expired' ? 'red' : 'blue'
                    }>
                      {incentive.status}
                    </Badge>
                  </Td>
                  <Td>
                    {incentive.earned_at && new Date(incentive.earned_at).toLocaleDateString()}
                    {incentive.redeemed_at && ` (Redeemed: ${new Date(incentive.redeemed_at).toLocaleDateString()})`}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>
      </Stack>

      {/* Add Metric Modal */}
      <Modal isOpen={isMetricModalOpen} onClose={onMetricModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Adherence Metric</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <form onSubmit={handleSubmitMetric(onSubmitMetric)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!metricErrors.type}>
                  <FormLabel>Type</FormLabel>
                  <Select {...registerMetric('type')}>
                    <option value="">Select type</option>
                    <option value="medication">Medication</option>
                    <option value="appointment">Appointment</option>
                    <option value="lifestyle">Lifestyle</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!metricErrors.target}>
                  <FormLabel>Target</FormLabel>
                  <Input
                    type="number"
                    {...registerMetric('target', { valueAsNumber: true })}
                  />
                </FormControl>

                <FormControl isInvalid={!!metricErrors.period}>
                  <FormLabel>Period</FormLabel>
                  <Select {...registerMetric('period')}>
                    <option value="">Select period</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!metricErrors.start_date}>
                  <FormLabel>Start Date</FormLabel>
                  <Input
                    type="date"
                    {...registerMetric('start_date')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>End Date (Optional)</FormLabel>
                  <Input
                    type="date"
                    {...registerMetric('end_date')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <Textarea {...registerMetric('notes')} />
                </FormControl>

                <Button type="submit" colorScheme="blue">
                  Add Metric
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Add Incentive Modal */}
      <Modal isOpen={isIncentiveModalOpen} onClose={onIncentiveModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Incentive</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <form onSubmit={handleSubmitIncentive(onSubmitIncentive)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!incentiveErrors.type}>
                  <FormLabel>Type</FormLabel>
                  <Select {...registerIncentive('type')}>
                    <option value="">Select type</option>
                    <option value="monetary">Monetary</option>
                    <option value="non_monetary">Non-Monetary</option>
                    <option value="recognition">Recognition</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!incentiveErrors.value}>
                  <FormLabel>Value</FormLabel>
                  <Input {...registerIncentive('value')} />
                </FormControl>

                <FormControl isInvalid={!!incentiveErrors.description}>
                  <FormLabel>Description</FormLabel>
                  <Textarea {...registerIncentive('description')} />
                </FormControl>

                <FormControl isInvalid={!!incentiveErrors.criteria?.metric_type}>
                  <FormLabel>Metric Type</FormLabel>
                  <Select {...registerIncentive('criteria.metric_type')}>
                    <option value="">Select metric type</option>
                    <option value="medication">Medication</option>
                    <option value="appointment">Appointment</option>
                    <option value="lifestyle">Lifestyle</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!incentiveErrors.criteria?.target_value}>
                  <FormLabel>Target Value</FormLabel>
                  <Input
                    type="number"
                    {...registerIncentive('criteria.target_value', { valueAsNumber: true })}
                  />
                </FormControl>

                <FormControl isInvalid={!!incentiveErrors.criteria?.period}>
                  <FormLabel>Period</FormLabel>
                  <Select {...registerIncentive('criteria.period')}>
                    <option value="">Select period</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Expiry Date (Optional)</FormLabel>
                  <Input
                    type="date"
                    {...registerIncentive('expiry_date')}
                  />
                </FormControl>

                <Button type="submit" colorScheme="blue">
                  Add Incentive
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 