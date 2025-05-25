import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Input,
  InputGroup,
  InputLeftElement,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Stack,
  Select,
  Flex,
  Text,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import { FiSearch, FiPlus, FiMoreVertical, FiEdit2, FiTrash2, FiEye } from 'react-icons/fi';
import { usePatient } from '../../hooks/usePatient';
import { PatientRegistrationForm } from './PatientRegistrationForm';
import { Patient } from '../../types/patient';
import { useNavigate } from 'react-router-dom';

export const PatientList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<Patient['status'] | 'all'>('all');
  const [page, setPage] = useState(1);
  const [limit] = useState(10);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    patients,
    totalPatients,
    isLoading,
    searchPatients,
    deletePatient,
  } = usePatient();

  useEffect(() => {
    searchPatients({
      query: searchQuery,
      filters: statusFilter !== 'all' ? { status: statusFilter } : undefined,
      page,
      limit,
    });
  }, [searchQuery, statusFilter, page, limit, searchPatients]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1);
  };

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as Patient['status'] | 'all');
    setPage(1);
  };

  const handleDelete = async (id: string) => {
    try {
      await deletePatient(id);
      toast({
        title: 'Patient deleted successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const totalPages = Math.ceil(totalPatients / limit);

  return (
    <Box>
      <Stack spacing={4} mb={4}>
        <Flex justify="space-between" align="center">
          <InputGroup maxW="400px">
            <InputLeftElement pointerEvents="none">
              <FiSearch color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search patients..."
              value={searchQuery}
              onChange={handleSearch}
            />
          </InputGroup>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            onClick={onOpen}
          >
            New Patient
          </Button>
        </Flex>

        <Flex gap={4}>
          <Select
            value={statusFilter}
            onChange={handleStatusFilter}
            maxW="200px"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deceased">Deceased</option>
          </Select>
        </Flex>
      </Stack>

      <Box overflowX="auto">
        <Table>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Age</Th>
              <Th>Contact</Th>
              <Th>Status</Th>
              <Th>Flags</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {patients.map((patient) => (
              <Tr key={patient.id}>
                <Td>
                  {patient.first_name} {patient.last_name}
                </Td>
                <Td>
                  {new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()}
                </Td>
                <Td>{patient.contact_info.phone}</Td>
                <Td>
                  <Badge
                    colorScheme={
                      patient.status === 'active'
                        ? 'green'
                        : patient.status === 'inactive'
                        ? 'yellow'
                        : 'red'
                    }
                  >
                    {patient.status}
                  </Badge>
                </Td>
                <Td>
                  <Stack direction="row" spacing={2}>
                    {patient.flags.high_risk && (
                      <Badge colorScheme="red">High Risk</Badge>
                    )}
                    {patient.flags.special_needs && (
                      <Badge colorScheme="purple">Special Needs</Badge>
                    )}
                    {patient.flags.requires_follow_up && (
                      <Badge colorScheme="orange">Follow-up</Badge>
                    )}
                  </Stack>
                </Td>
                <Td>
                  <Menu>
                    <MenuButton
                      as={IconButton}
                      icon={<FiMoreVertical />}
                      variant="ghost"
                      size="sm"
                    />
                    <MenuList>
                      <MenuItem
                        icon={<FiEye />}
                        onClick={() => navigate(`/patients/${patient.id}`)}
                      >
                        View Details
                      </MenuItem>
                      <MenuItem
                        icon={<FiEdit2 />}
                        onClick={() => navigate(`/patients/${patient.id}/edit`)}
                      >
                        Edit
                      </MenuItem>
                      <MenuDivider />
                      <MenuItem
                        icon={<FiTrash2 />}
                        color="red.500"
                        onClick={() => handleDelete(patient.id)}
                      >
                        Delete
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {totalPages > 1 && (
        <Flex justify="center" mt={4} gap={2}>
          <Button
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            isDisabled={page === 1}
          >
            Previous
          </Button>
          <Text>
            Page {page} of {totalPages}
          </Text>
          <Button
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            isDisabled={page === totalPages}
          >
            Next
          </Button>
        </Flex>
      )}

      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Register New Patient</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <PatientRegistrationForm
              onSuccess={() => {
                onClose();
                searchPatients({
                  query: searchQuery,
                  filters: statusFilter !== 'all' ? { status: statusFilter } : undefined,
                  page,
                  limit,
                });
              }}
              onCancel={onClose}
            />
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 