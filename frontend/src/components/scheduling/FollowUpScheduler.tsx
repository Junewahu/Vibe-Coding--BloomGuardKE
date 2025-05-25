import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Heading,
  Stack,
  Text,
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  Select,
  IconButton,
  Badge,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format, addDays, addMonths } from 'date-fns';
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

interface FollowUp {
  id: string;
  patient_id: string;
  type: 'immunization' | 'milestone' | 'post_operative' | 'chronic_care';
  scheduled_date: string;
  status: 'scheduled' | 'completed' | 'missed' | 'cancelled';
  notes?: string;
  protocol_id?: string;
  reminder_settings: {
    sms: boolean;
    whatsapp: boolean;
    voice: boolean;
    ussd: boolean;
    reminder_days: number[];
  };
}

const followUpSchema = z.object({
  type: z.enum(['immunization', 'milestone', 'post_operative', 'chronic_care']),
  scheduled_date: z.string().min(1, 'Date is required'),
  notes: z.string().optional(),
  protocol_id: z.string().optional(),
  reminder_settings: z.object({
    sms: z.boolean(),
    whatsapp: z.boolean(),
    voice: z.boolean(),
    ussd: z.boolean(),
    reminder_days: z.array(z.number()),
  }),
});

type FollowUpFormData = z.infer<typeof followUpSchema>;

export const FollowUpScheduler: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [followUps, setFollowUps] = useState<FollowUp[]>([]);
  const { currentPatient, getPatient } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FollowUpFormData>({
    resolver: zodResolver(followUpSchema),
  });

  useEffect(() => {
    loadPatientAndFollowUps();
  }, [id]);

  const loadPatientAndFollowUps = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      // TODO: Implement getFollowUps in patientStore
      // const followUps = await getFollowUps(id);
      // setFollowUps(followUps);
    } catch (error) {
      toast({
        title: 'Error loading follow-ups',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFollowUp = () => {
    reset();
    onOpen();
  };

  const onSubmit = async (data: FollowUpFormData) => {
    if (!id) return;
    try {
      // TODO: Implement createFollowUp in patientStore
      // await createFollowUp(id, data);
      toast({
        title: 'Follow-up scheduled successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      loadPatientAndFollowUps();
    } catch (error) {
      toast({
        title: 'Error scheduling follow-up',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'scheduled':
        return 'blue';
      case 'missed':
        return 'red';
      case 'cancelled':
        return 'gray';
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
          <Heading size="lg">Follow-Up Schedule</Heading>
          <Flex gap={2}>
            <Button colorScheme="blue" onClick={handleCreateFollowUp}>
              Schedule Follow-Up
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
          <CardBody>
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Type</Th>
                  <Th>Scheduled Date</Th>
                  <Th>Status</Th>
                  <Th>Reminder Settings</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {followUps.map((followUp) => (
                  <Tr key={followUp.id}>
                    <Td>{followUp.type}</Td>
                    <Td>{format(new Date(followUp.scheduled_date), 'MMM d, yyyy')}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(followUp.status)}>
                        {followUp.status}
                      </Badge>
                    </Td>
                    <Td>
                      <Flex gap={1}>
                        {followUp.reminder_settings.sms && (
                          <Badge colorScheme="blue">SMS</Badge>
                        )}
                        {followUp.reminder_settings.whatsapp && (
                          <Badge colorScheme="green">WhatsApp</Badge>
                        )}
                        {followUp.reminder_settings.voice && (
                          <Badge colorScheme="purple">Voice</Badge>
                        )}
                        {followUp.reminder_settings.ussd && (
                          <Badge colorScheme="orange">USSD</Badge>
                        )}
                      </Flex>
                    </Td>
                    <Td>
                      <Flex gap={2}>
                        <IconButton
                          aria-label="Edit follow-up"
                          icon={<EditIcon />}
                          size="sm"
                          onClick={() => {/* TODO: Implement edit */}}
                        />
                        <IconButton
                          aria-label="Delete follow-up"
                          icon={<DeleteIcon />}
                          size="sm"
                          colorScheme="red"
                          onClick={() => {/* TODO: Implement delete */}}
                        />
                      </Flex>
                    </Td>
                  </Tr>
                ))}
                {followUps.length === 0 && (
                  <Tr>
                    <Td colSpan={5} textAlign="center">
                      No follow-ups scheduled
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>

      {/* Schedule Follow-Up Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Schedule Follow-Up</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.type}>
                  <FormLabel>Follow-Up Type</FormLabel>
                  <Select {...register('type')}>
                    <option value="">Select type</option>
                    <option value="immunization">Immunization</option>
                    <option value="milestone">Milestone Check</option>
                    <option value="post_operative">Post-Operative Visit</option>
                    <option value="chronic_care">Chronic Care</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.scheduled_date}>
                  <FormLabel>Scheduled Date</FormLabel>
                  <Input
                    type="date"
                    {...register('scheduled_date')}
                    min={format(new Date(), 'yyyy-MM-dd')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Input {...register('notes')} placeholder="Add any notes about the follow-up" />
                </FormControl>

                <FormControl>
                  <FormLabel>Protocol</FormLabel>
                  <Select {...register('protocol_id')}>
                    <option value="">Select protocol</option>
                    <option value="standard">Standard Protocol</option>
                    <option value="custom">Custom Protocol</option>
                  </Select>
                </FormControl>

                <Heading size="sm" mt={4}>Reminder Settings</Heading>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <GridItem>
                    <FormControl>
                      <FormLabel>SMS</FormLabel>
                      <Select {...register('reminder_settings.sms')}>
                        <option value="true">Enabled</option>
                        <option value="false">Disabled</option>
                      </Select>
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel>WhatsApp</FormLabel>
                      <Select {...register('reminder_settings.whatsapp')}>
                        <option value="true">Enabled</option>
                        <option value="false">Disabled</option>
                      </Select>
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel>Voice</FormLabel>
                      <Select {...register('reminder_settings.voice')}>
                        <option value="true">Enabled</option>
                        <option value="false">Disabled</option>
                      </Select>
                    </FormControl>
                  </GridItem>
                  <GridItem>
                    <FormControl>
                      <FormLabel>USSD</FormLabel>
                      <Select {...register('reminder_settings.ussd')}>
                        <option value="true">Enabled</option>
                        <option value="false">Disabled</option>
                      </Select>
                    </FormControl>
                  </GridItem>
                </Grid>

                <Button type="submit" colorScheme="blue" mr={3}>
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