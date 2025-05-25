import React, { useEffect, useState } from 'react';
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
  Badge,
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
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { Immunization } from '../../types/patient';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

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
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
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
      toast({
        title: 'Error loading immunizations',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddImmunization = () => {
    reset();
    onOpen();
  };

  const onSubmit = async (data: ImmunizationFormData) => {
    if (!id) return;
    try {
      await createImmunization(id, data);
      toast({
        title: 'Immunization record created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      loadPatientAndImmunizations();
    } catch (error) {
      toast({
        title: 'Error creating immunization record',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
          <CardBody>
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Vaccine</Th>
                  <Th>Scheduled Date</Th>
                  <Th>Administered Date</Th>
                  <Th>Status</Th>
                  <Th>Batch Number</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {immunizations.map((immunization) => (
                  <Tr key={immunization.id}>
                    <Td>{immunization.vaccine_name}</Td>
                    <Td>{format(new Date(immunization.scheduled_date), 'PPP')}</Td>
                    <Td>
                      {immunization.administered_date
                        ? format(new Date(immunization.administered_date), 'PPP')
                        : 'Not administered'}
                    </Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(immunization.status)}>
                        {immunization.status}
                      </Badge>
                    </Td>
                    <Td>{immunization.batch_number || 'N/A'}</Td>
                    <Td>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="ghost"
                        onClick={() => {/* TODO: Implement view immunization details */}}
                      >
                        View
                      </Button>
                    </Td>
                  </Tr>
                ))}
                {immunizations.length === 0 && (
                  <Tr>
                    <Td colSpan={6} textAlign="center">
                      No immunization records found
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>

      {/* Add Immunization Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Immunization Record</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.vaccine_name}>
                  <FormLabel>Vaccine Name</FormLabel>
                  <Select {...register('vaccine_name')}>
                    <option value="">Select vaccine</option>
                    <option value="bcg">BCG</option>
                    <option value="polio">Polio</option>
                    <option value="dpt">DPT</option>
                    <option value="measles">Measles</option>
                    <option value="hepatitis_b">Hepatitis B</option>
                    <option value="pneumococcal">Pneumococcal</option>
                    <option value="rotavirus">Rotavirus</option>
                    <option value="influenza">Influenza</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.scheduled_date}>
                  <FormLabel>Scheduled Date</FormLabel>
                  <Input type="date" {...register('scheduled_date')} />
                </FormControl>

                <FormControl>
                  <FormLabel>Administered Date</FormLabel>
                  <Input type="date" {...register('administered_date')} />
                </FormControl>

                <FormControl>
                  <FormLabel>Batch Number</FormLabel>
                  <Input {...register('batch_number')} placeholder="Enter batch number" />
                </FormControl>

                <FormControl>
                  <FormLabel>Administered By</FormLabel>
                  <Input {...register('administered_by')} placeholder="Enter name of healthcare provider" />
                </FormControl>

                <FormControl isInvalid={!!errors.status}>
                  <FormLabel>Status</FormLabel>
                  <Select {...register('status')}>
                    <option value="">Select status</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="missed">Missed</option>
                  </Select>
                </FormControl>

                <Button type="submit" colorScheme="blue" mr={3}>
                  Save Record
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 