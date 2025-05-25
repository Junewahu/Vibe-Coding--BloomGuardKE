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
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useParams } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';

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

  const { isOpen: isCaregiverModalOpen, onOpen: onCaregiverModalOpen, onClose: onCaregiverModalClose } = useDisclosure();
  const { isOpen: isInteractionModalOpen, onOpen: onInteractionModalOpen, onClose: onInteractionModalClose } = useDisclosure();
  const toast = useToast();

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
      toast({
        title: 'Error',
        description: 'Failed to load caregivers and interactions',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      onCaregiverModalClose();
      resetCaregiver();
      toast({
        title: 'Success',
        description: 'Caregiver added successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add caregiver',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      onInteractionModalClose();
      resetInteraction();
      calculateStats([...interactions, newInteraction]);
      toast({
        title: 'Success',
        description: 'Interaction scheduled successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to schedule interaction',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
      toast({
        title: 'Success',
        description: 'Interaction status updated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update interaction status',
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
          <Heading size="lg">Caregiver Engagement</Heading>
          <Stack direction="row">
            <Button colorScheme="blue" onClick={onCaregiverModalOpen}>
              Add Caregiver
            </Button>
            <Button colorScheme="green" onClick={onInteractionModalOpen}>
              Schedule Interaction
            </Button>
          </Stack>
        </Flex>

        <Grid templateColumns="repeat(4, 1fr)" gap={4}>
          <Stat>
            <StatLabel>Total Interactions</StatLabel>
            <StatNumber>{stats.totalInteractions}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Completed</StatLabel>
            <StatNumber>{stats.completedInteractions}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Upcoming</StatLabel>
            <StatNumber>{stats.upcomingInteractions}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Interaction Trend</StatLabel>
            <StatNumber>
              {stats.interactionTrend > 0 ? '+' : ''}{stats.interactionTrend.toFixed(1)}%
            </StatNumber>
            <StatHelpText>
              <StatArrow type={stats.interactionTrend >= 0 ? 'increase' : 'decrease'} />
              vs last month
            </StatHelpText>
          </Stat>
        </Grid>

        <Card p={4}>
          <Heading size="md" mb={4}>Caregivers</Heading>
          <Table>
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Relationship</Th>
                <Th>Contact</Th>
                <Th>Status</Th>
              </Tr>
            </Thead>
            <Tbody>
              {caregivers.map(caregiver => (
                <Tr key={caregiver.id}>
                  <Td>{caregiver.name}</Td>
                  <Td>{caregiver.relationship}</Td>
                  <Td>{caregiver.phone}</Td>
                  <Td>
                    <Badge colorScheme={caregiver.is_primary ? 'green' : 'gray'}>
                      {caregiver.is_primary ? 'Primary' : 'Secondary'}
                    </Badge>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>

        <Card p={4}>
          <Heading size="md" mb={4}>Recent Interactions</Heading>
          <Table>
            <Thead>
              <Tr>
                <Th>Type</Th>
                <Th>Date</Th>
                <Th>Status</Th>
                <Th>Notes</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {interactions.map(interaction => (
                <Tr key={interaction.id}>
                  <Td>{interaction.type}</Td>
                  <Td>{new Date(interaction.scheduled_date).toLocaleDateString()}</Td>
                  <Td>
                    <Badge colorScheme={
                      interaction.status === 'completed' ? 'green' :
                      interaction.status === 'scheduled' ? 'blue' :
                      interaction.status === 'cancelled' ? 'red' : 'gray'
                    }>
                      {interaction.status}
                    </Badge>
                  </Td>
                  <Td>{interaction.notes}</Td>
                  <Td>
                    {interaction.status === 'scheduled' && (
                      <Stack direction="row">
                        <Button
                          size="sm"
                          colorScheme="green"
                          onClick={() => updateInteractionStatus(interaction.id, 'completed')}
                        >
                          Complete
                        </Button>
                        <Button
                          size="sm"
                          colorScheme="red"
                          onClick={() => updateInteractionStatus(interaction.id, 'cancelled')}
                        >
                          Cancel
                        </Button>
                      </Stack>
                    )}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>
      </Stack>

      {/* Add Caregiver Modal */}
      <Modal isOpen={isCaregiverModalOpen} onClose={onCaregiverModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Caregiver</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <form onSubmit={handleSubmitCaregiver(onSubmitCaregiver)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!caregiverErrors.name}>
                  <FormLabel>Name</FormLabel>
                  <Input {...registerCaregiver('name')} />
                </FormControl>

                <FormControl isInvalid={!!caregiverErrors.relationship}>
                  <FormLabel>Relationship</FormLabel>
                  <Select {...registerCaregiver('relationship')}>
                    <option value="">Select relationship</option>
                    <option value="Spouse">Spouse</option>
                    <option value="Child">Child</option>
                    <option value="Parent">Parent</option>
                    <option value="Sibling">Sibling</option>
                    <option value="Other">Other</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!caregiverErrors.phone}>
                  <FormLabel>Phone</FormLabel>
                  <Input {...registerCaregiver('phone')} />
                </FormControl>

                <FormControl isInvalid={!!caregiverErrors.email}>
                  <FormLabel>Email (Optional)</FormLabel>
                  <Input {...registerCaregiver('email')} />
                </FormControl>

                <FormControl>
                  <FormLabel>Address (Optional)</FormLabel>
                  <Textarea {...registerCaregiver('address')} />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <Textarea {...registerCaregiver('notes')} />
                </FormControl>

                <Button type="submit" colorScheme="blue">
                  Add Caregiver
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Schedule Interaction Modal */}
      <Modal isOpen={isInteractionModalOpen} onClose={onInteractionModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Schedule Interaction</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <form onSubmit={handleSubmitInteraction(onSubmitInteraction)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!interactionErrors.type}>
                  <FormLabel>Type</FormLabel>
                  <Select {...registerInteraction('type')}>
                    <option value="">Select type</option>
                    <option value="visit">Visit</option>
                    <option value="call">Call</option>
                    <option value="message">Message</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!interactionErrors.scheduled_date}>
                  <FormLabel>Scheduled Date</FormLabel>
                  <Input
                    type="datetime-local"
                    {...registerInteraction('scheduled_date')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <Textarea {...registerInteraction('notes')} />
                </FormControl>

                <Button type="submit" colorScheme="blue">
                  Schedule
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 