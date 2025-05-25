import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Grid,
  Heading,
  Icon,
  IconButton,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Stack,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useDisclosure,
  useToast,
  VStack,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Divider,
  Badge,
  FormControl,
  FormLabel,
  Input,
  Textarea,
} from '@chakra-ui/react';
import { FiCalendar, FiMapPin, FiPlus, FiEye } from 'react-icons/fi';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCHWContext } from '../../contexts/CHWContext';
import { FieldVisit } from '../../types/chw';

const fieldVisitSchema = z.object({
  patient_id: z.string().min(1, 'Patient is required'),
  visit_type: z.enum(['home_visit', 'follow_up', 'emergency', 'routine']),
  scheduled_date: z.string().min(1, 'Date is required'),
  notes: z.string().optional(),
  location: z.object({
    latitude: z.number(),
    longitude: z.number(),
    address: z.string(),
  }).optional(),
});

type FieldVisitFormData = z.infer<typeof fieldVisitSchema>;

export const CHWFieldTracker: React.FC = () => {
  const { isOpen: isVisitModalOpen, onOpen: onVisitModalOpen, onClose: onVisitModalClose } = useDisclosure();
  const { isOpen: isDetailsOpen, onOpen: onDetailsOpen, onClose: onDetailsClose } = useDisclosure();
  const [selectedVisit, setSelectedVisit] = useState<FieldVisit | null>(null);
  const toast = useToast();

  const {
    fieldVisits,
    stats,
    isLoading,
    loadFieldData,
    createFieldVisit,
    updateFieldVisit,
  } = useCHWContext();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FieldVisitFormData>({
    resolver: zodResolver(fieldVisitSchema),
  });

  useEffect(() => {
    loadFieldData();
  }, [loadFieldData]);

  const onSubmit = async (data: FieldVisitFormData) => {
    try {
      await createFieldVisit({
        ...data,
        status: 'scheduled',
      });
      onVisitModalClose();
      reset();
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleVisitStatusUpdate = async (visitId: string, newStatus: FieldVisit['status']) => {
    try {
      await updateFieldVisit(visitId, { status: newStatus });
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleViewVisitDetails = (visit: FieldVisit) => {
    setSelectedVisit(visit);
    onDetailsOpen();
  };

  if (isLoading) {
    return (
      <Box p={4}>
        <Text>Loading...</Text>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Grid templateColumns="repeat(4, 1fr)" gap={4} mb={6}>
        <Card>
          <CardBody>
            <VStack align="start" spacing={2}>
              <Text color="gray.500">Total Visits</Text>
              <Heading size="lg">{stats.totalVisits}</Heading>
              <Text color={stats.visitTrend >= 0 ? 'green.500' : 'red.500'}>
                {stats.visitTrend >= 0 ? '+' : ''}{stats.visitTrend}% from last month
              </Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="start" spacing={2}>
              <Text color="gray.500">Completed Visits</Text>
              <Heading size="lg">{stats.completedVisits}</Heading>
              <Text color="blue.500">
                {((stats.completedVisits / stats.totalVisits) * 100).toFixed(1)}% completion rate
              </Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody>
            <VStack align="start" spacing={2}>
              <Text color="gray.500">Scheduled Activities</Text>
              <Heading size="lg">{stats.scheduledActivities}</Heading>
              <Text color="purple.500">Upcoming events</Text>
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">Field Visits</Heading>
        <Button
          leftIcon={<Icon as={FiPlus} />}
          colorScheme="blue"
          onClick={onVisitModalOpen}
        >
          Schedule Visit
        </Button>
      </Flex>

      <Card>
        <CardBody>
          <Table>
            <Thead>
              <Tr>
                <Th>Date</Th>
                <Th>Type</Th>
                <Th>Status</Th>
                <Th>Location</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {fieldVisits.map((visit) => (
                <Tr key={visit.id}>
                  <Td>{new Date(visit.scheduled_date).toLocaleDateString()}</Td>
                  <Td>{visit.visit_type.replace('_', ' ')}</Td>
                  <Td>
                    <Badge
                      colorScheme={
                        visit.status === 'completed'
                          ? 'green'
                          : visit.status === 'in_progress'
                          ? 'blue'
                          : visit.status === 'cancelled'
                          ? 'red'
                          : 'gray'
                      }
                    >
                      {visit.status.replace('_', ' ')}
                    </Badge>
                  </Td>
                  <Td>{visit.location?.address || 'Not specified'}</Td>
                  <Td>
                    <IconButton
                      aria-label="View details"
                      icon={<Icon as={FiEye} />}
                      size="sm"
                      mr={2}
                      onClick={() => handleViewVisitDetails(visit)}
                    />
                    {visit.status === 'scheduled' && (
                      <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={() => handleVisitStatusUpdate(visit.id, 'in_progress')}
                      >
                        Start Visit
                      </Button>
                    )}
                    {visit.status === 'in_progress' && (
                      <Button
                        size="sm"
                        colorScheme="green"
                        onClick={() => handleVisitStatusUpdate(visit.id, 'completed')}
                      >
                        Complete
                      </Button>
                    )}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>

      {/* Schedule Visit Modal */}
      <Modal isOpen={isVisitModalOpen} onClose={onVisitModalClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Schedule Field Visit</ModalHeader>
          <ModalCloseButton />
          <form onSubmit={handleSubmit(onSubmit)}>
            <ModalBody>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.patient_id}>
                  <FormLabel>Patient</FormLabel>
                  <Select {...register('patient_id')}>
                    <option value="">Select Patient</option>
                    {/* TODO: Add patient options */}
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.visit_type}>
                  <FormLabel>Visit Type</FormLabel>
                  <Select {...register('visit_type')}>
                    <option value="home_visit">Home Visit</option>
                    <option value="follow_up">Follow-up</option>
                    <option value="emergency">Emergency</option>
                    <option value="routine">Routine</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.scheduled_date}>
                  <FormLabel>Date & Time</FormLabel>
                  <Input
                    type="datetime-local"
                    {...register('scheduled_date')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Textarea {...register('notes')} />
                </FormControl>
              </Stack>
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onVisitModalClose}>
                Cancel
              </Button>
              <Button
                colorScheme="blue"
                type="submit"
                isLoading={isSubmitting}
              >
                Schedule Visit
              </Button>
            </ModalFooter>
          </form>
        </ModalContent>
      </Modal>

      {/* Visit Details Drawer */}
      <Drawer isOpen={isDetailsOpen} placement="right" onClose={onDetailsClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Visit Details</DrawerHeader>

          <DrawerBody>
            {selectedVisit && (
              <Stack spacing={4}>
                <Box>
                  <Text fontWeight="bold">Date</Text>
                  <Text>{new Date(selectedVisit.scheduled_date).toLocaleString()}</Text>
                </Box>

                <Box>
                  <Text fontWeight="bold">Type</Text>
                  <Text>{selectedVisit.visit_type.replace('_', ' ')}</Text>
                </Box>

                <Box>
                  <Text fontWeight="bold">Status</Text>
                  <Badge
                    colorScheme={
                      selectedVisit.status === 'completed'
                        ? 'green'
                        : selectedVisit.status === 'in_progress'
                        ? 'blue'
                        : selectedVisit.status === 'cancelled'
                        ? 'red'
                        : 'gray'
                    }
                  >
                    {selectedVisit.status.replace('_', ' ')}
                  </Badge>
                </Box>

                {selectedVisit.location && (
                  <Box>
                    <Text fontWeight="bold">Location</Text>
                    <Text>{selectedVisit.location.address}</Text>
                  </Box>
                )}

                {selectedVisit.notes && (
                  <Box>
                    <Text fontWeight="bold">Notes</Text>
                    <Text>{selectedVisit.notes}</Text>
                  </Box>
                )}

                <Divider />

                <Button
                  colorScheme="blue"
                  onClick={() => {
                    // TODO: Implement navigation to patient details
                  }}
                >
                  View Patient Details
                </Button>
              </Stack>
            )}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
}; 