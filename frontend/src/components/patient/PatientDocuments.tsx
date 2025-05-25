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
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format } from 'date-fns';
import { DownloadIcon, DeleteIcon, ViewIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

interface Document {
  id: string;
  patient_id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  uploaded_by: string;
  status: 'pending' | 'verified' | 'rejected';
  notes?: string;
}

const documentSchema = z.object({
  document_type: z.string().min(1, 'Document type is required'),
  file: z.instanceof(File).optional(),
  notes: z.string().optional(),
});

type DocumentFormData = z.infer<typeof documentSchema>;

export const PatientDocuments: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [documents, setDocuments] = useState<Document[]>([]);
  const { currentPatient, getPatient } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DocumentFormData>({
    resolver: zodResolver(documentSchema),
  });

  useEffect(() => {
    loadPatientAndDocuments();
  }, [id]);

  const loadPatientAndDocuments = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      // TODO: Implement getDocuments in patientStore
      // const docs = await getDocuments(id);
      // setDocuments(docs);
    } catch (error) {
      toast({
        title: 'Error loading documents',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadDocument = () => {
    reset();
    onOpen();
  };

  const onSubmit = async (data: DocumentFormData) => {
    if (!id || !data.file) return;
    try {
      // TODO: Implement uploadDocument in patientStore
      // await uploadDocument(id, data);
      toast({
        title: 'Document uploaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      loadPatientAndDocuments();
    } catch (error) {
      toast({
        title: 'Error uploading document',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleDownload = async (documentId: string) => {
    try {
      // TODO: Implement downloadDocument in patientStore
      // await downloadDocument(documentId);
      toast({
        title: 'Document downloaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error downloading document',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      // TODO: Implement deleteDocument in patientStore
      // await deleteDocument(documentId);
      toast({
        title: 'Document deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      loadPatientAndDocuments();
    } catch (error) {
      toast({
        title: 'Error deleting document',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'green';
      case 'pending':
        return 'yellow';
      case 'rejected':
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
          <Heading size="lg">Patient Documents</Heading>
          <Flex gap={2}>
            <Button colorScheme="blue" onClick={handleUploadDocument}>
              Upload Document
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
                  <Th>Document Type</Th>
                  <Th>File Name</Th>
                  <Th>Size</Th>
                  <Th>Uploaded</Th>
                  <Th>Status</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {documents.map((doc) => (
                  <Tr key={doc.id}>
                    <Td>{doc.document_type}</Td>
                    <Td>{doc.file_name}</Td>
                    <Td>{(doc.file_size / 1024).toFixed(2)} KB</Td>
                    <Td>{format(new Date(doc.uploaded_at), 'MMM d, yyyy')}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(doc.status)}>
                        {doc.status}
                      </Badge>
                    </Td>
                    <Td>
                      <Flex gap={2}>
                        <IconButton
                          aria-label="View document"
                          icon={<ViewIcon />}
                          size="sm"
                          onClick={() => {/* TODO: Implement view document */}}
                        />
                        <IconButton
                          aria-label="Download document"
                          icon={<DownloadIcon />}
                          size="sm"
                          onClick={() => handleDownload(doc.id)}
                        />
                        <IconButton
                          aria-label="Delete document"
                          icon={<DeleteIcon />}
                          size="sm"
                          colorScheme="red"
                          onClick={() => handleDelete(doc.id)}
                        />
                      </Flex>
                    </Td>
                  </Tr>
                ))}
                {documents.length === 0 && (
                  <Tr>
                    <Td colSpan={6} textAlign="center">
                      No documents found
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>

      {/* Upload Document Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload Document</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <Stack spacing={4}>
                <FormControl isInvalid={!!errors.document_type}>
                  <FormLabel>Document Type</FormLabel>
                  <Select {...register('document_type')}>
                    <option value="">Select document type</option>
                    <option value="id_card">ID Card</option>
                    <option value="insurance">Insurance Card</option>
                    <option value="medical_report">Medical Report</option>
                    <option value="prescription">Prescription</option>
                    <option value="lab_result">Lab Result</option>
                    <option value="xray">X-Ray</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>File</FormLabel>
                  <Input
                    type="file"
                    {...register('file')}
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notes</FormLabel>
                  <Input {...register('notes')} placeholder="Add any notes about the document" />
                </FormControl>

                <Button type="submit" colorScheme="blue" mr={3}>
                  Upload
                </Button>
              </Stack>
            </form>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 