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
  Switch,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format } from 'date-fns';
import { AddIcon, EditIcon, DeleteIcon, RepeatIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

interface Reminder {
  id: string;
  follow_up_id: string;
  patient_id: string;
  type: 'sms' | 'whatsapp' | 'voice' | 'ussd';
  status: 'pending' | 'sent' | 'delivered' | 'failed';
  scheduled_time: string;
  message_template: string;
  retry_count: number;
  max_retries: number;
  response?: {
    received_at: string;
    action: 'confirmed' | 'cancelled' | 'rescheduled';
    notes?: string;
  };
}

const reminderSchema = z.object({
  type: z.enum(['sms', 'whatsapp', 'voice', 'ussd']),
  message_template: z.string().min(1, 'Message template is required'),
  scheduled_time: z.string().min(1, 'Scheduled time is required'),
  max_retries: z.number().min(0).max(5),
  retry_interval: z.number().min(1).max(24),
});

type ReminderFormData = z.infer<typeof reminderSchema>;

export const ReminderDispatch: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const { currentPatient, getPatient } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReminderFormData>({
    resolver: zodResolver(reminderSchema),
  });

  useEffect(() => {
    loadPatientAndReminders();
  }, [id]);

  const loadPatientAndReminders = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      // TODO: Implement getReminders in patientStore
      // const reminders = await getReminders(id);
      // setReminders(reminders);
    } catch (error) {
      toast({
        title: 'Error loading reminders',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateReminder = () => {
    reset();
    onOpen();
  };

  const onSubmit = async (data: ReminderFormData) => {
    if (!id) return;
    try {
      // TODO: Implement createReminder in patientStore
      // await createReminder(id, data);
      toast({
        title: 'Reminder scheduled successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      loadPatientAndReminders();
    } catch (error) {
      toast({
        title: 'Error scheduling reminder',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'green';
      case 'sent':
        return 'blue';
      case 'pending':
        return 'yellow';
      case 'failed':
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
          <Heading size="lg">Reminder Dispatch</Heading>
          <Flex gap={2}>
            <Button colorScheme="blue" onClick={handleCreateReminder}>
              Schedule Reminder
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
                  <Th>Scheduled Time</Th>
                  <Th>Status</Th>
                  <Th>Retries</Th>
                  <Th>Response</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {reminders.map((reminder) => (
                  <Tr key={reminder.id}>
                    <Td>
                      <Badge colorScheme={
                        reminder.type === 'sms' ? 'blue' :
                        reminder.type === 'whatsapp' ? 'green' :
                        reminder.type === 'voice' ? 'purple' : 'orange'
                      }>
                        {reminder.type.toUpperCase()}
                      </Badge>
                    </Td>
                    <Td>{format(new Date(reminder.scheduled_time), 'MMM d, yyyy HH:mm')}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(reminder.status)}>
                        {reminder.status}
                      </Badge>
                    </Td>
                    <Td>{reminder.retry_count}/{reminder.max_retries}</Td>
                    <Td>
                      {reminder.response ? (
                        <Badge colorScheme={
                          reminder.response.action === 'confirmed' ? 'green' :
                          reminder.response.action === 'cancelled' ? 'red' : 'yellow'
                        }>
                          {reminder.response.action}
                        </Badge>
                      ) : (
                        <Text color="gray.500">No response</Text>
                      )}
                    </Td>
                    <Td>
                      <Flex gap={2}>
                        <IconButton
                          aria-label="Edit reminder"
                          icon={<EditIcon />}
                          size="sm"
                          onClick={() => {/* TODO: Implement edit */}}
                        />
                        <IconButton
                          aria-label="Retry reminder"
                          icon={<RepeatIcon />}
                          size="sm"
                          colorScheme="blue"
                          onClick={() => {/* TODO: Implement retry */}}
                        />
                        <IconButton
                          aria-label="Delete reminder"
                          icon={<DeleteIcon />}
                          size="sm"
                          colorScheme="red"
                          onClick={() => {/* TODO: Implement delete */}}
                        />
                      </Flex>
                    </Td>
                  </Tr>
                ))}
                {reminders.length === 0 && (
                  <Tr>
                    <Td colSpan={6} textAlign="center">
                      No reminders scheduled
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>

      {/* Schedule Reminder Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Schedule Reminder</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.type}>
                  <FormLabel>Reminder Type</FormLabel>
                  <Select {...register('type')}>
                    <option value="">Select type</option>
                    <option value="sms">SMS</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="voice">Voice Call</option>
                    <option value="ussd">USSD</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.scheduled_time}>
                  <FormLabel>Scheduled Time</FormLabel>
                  <Input
                    type="datetime-local"
                    {...register('scheduled_time')}
                    min={format(new Date(), "yyyy-MM-dd'T'HH:mm")}
                  />
                </FormControl>

                <FormControl isInvalid={!!errors.message_template}>
                  <FormLabel>Message Template</FormLabel>
                  <Input
                    {...register('message_template')}
                    placeholder="Enter message template with {name}, {date}, etc."
                  />
                </FormControl>

                <FormControl isInvalid={!!errors.max_retries}>
                  <FormLabel>Maximum Retries</FormLabel>
                  <NumberInput min={0} max={5} defaultValue={3}>
                    <NumberInputField {...register('max_retries')} />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                <FormControl isInvalid={!!errors.retry_interval}>
                  <FormLabel>Retry Interval (hours)</FormLabel>
                  <NumberInput min={1} max={24} defaultValue={4}>
                    <NumberInputField {...register('retry_interval')} />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

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