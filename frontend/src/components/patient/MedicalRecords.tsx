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
  Textarea,
  Select,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { MedicalRecord } from '../../types/patient';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const medicalRecordSchema = z.object({
  record_type: z.string().min(1, 'Record type is required'),
  record_date: z.string().min(1, 'Date is required'),
  diagnosis: z.string().optional(),
  treatment: z.string().optional(),
  notes: z.string().optional(),
});

type MedicalRecordFormData = z.infer<typeof medicalRecordSchema>;

export const MedicalRecords: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const { currentPatient, getPatient, getMedicalRecords, createMedicalRecord } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MedicalRecordFormData>({
    resolver: zodResolver(medicalRecordSchema),
  });

  useEffect(() => {
    loadPatientAndRecords();
  }, [id]);

  const loadPatientAndRecords = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      const records = await getMedicalRecords(id);
      setRecords(records);
    } catch (error) {
      toast({
        title: 'Error loading records',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRecord = () => {
    reset();
    onOpen();
  };

  const onSubmit = async (data: MedicalRecordFormData) => {
    if (!id) return;
    try {
      await createMedicalRecord(id, data);
      toast({
        title: 'Medical record created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      loadPatientAndRecords();
    } catch (error) {
      toast({
        title: 'Error creating medical record',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
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
          <Heading size="lg">Medical Records</Heading>
          <Flex gap={2}>
            <Button colorScheme="blue" onClick={handleAddRecord}>
              Add Record
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
                  <Th>Date</Th>
                  <Th>Type</Th>
                  <Th>Diagnosis</Th>
                  <Th>Treatment</Th>
                  <Th>Status</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {records.map((record) => (
                  <Tr key={record.id}>
                    <Td>{format(new Date(record.record_date), 'PPP')}</Td>
                    <Td>{record.record_type}</Td>
                    <Td>{record.diagnosis || 'N/A'}</Td>
                    <Td>{record.treatment || 'N/A'}</Td>
                    <Td>
                      <Badge colorScheme="green">Completed</Badge>
                    </Td>
                    <Td>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="ghost"
                        onClick={() => {/* TODO: Implement view record details */}}
                      >
                        View
                      </Button>
                    </Td>
                  </Tr>
                ))}
                {records.length === 0 && (
                  <Tr>
                    <Td colSpan={6} textAlign="center">
                      No medical records found
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>

      {/* Add Record Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Medical Record</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.record_type}>
                  <FormLabel>Record Type</FormLabel>
                  <Select {...register('record_type')}>
                    <option value="">Select record type</option>
                    <option value="consultation">Consultation</option>
                    <option value="procedure">Procedure</option>
                    <option value="test">Test</option>
                    <option value="prescription">Prescription</option>
                  </Select>
                </FormControl>

                <FormControl isInvalid={!!errors.record_date}>
                  <FormLabel>Date</FormLabel>
                  <Input type="date" {...register('record_date')} />
                </FormControl>

                <FormControl>
                  <FormLabel>Diagnosis</FormLabel>
                  <Textarea {...register('diagnosis')} placeholder="Enter diagnosis details" />
                </FormControl>

                <FormControl>
                  <FormLabel>Treatment</FormLabel>
                  <Textarea {...register('treatment')} placeholder="Enter treatment details" />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Textarea {...register('notes')} placeholder="Additional notes" />
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