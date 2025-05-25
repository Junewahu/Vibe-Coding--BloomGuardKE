import React, { useEffect, useState } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  useToast,
  Badge,
  Text,
  Spinner,
  Flex,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react';
import { SearchIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { Patient, PatientStatus } from '../../types/patient';

const statusColors: Record<PatientStatus, string> = {
  active: 'green',
  inactive: 'gray',
  deceased: 'red',
  transferred: 'blue',
};

export const PatientList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const { patients, isLoading, error, getPatients, searchPatients } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      await getPatients();
    } catch (error) {
      toast({
        title: 'Error loading patients',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      await loadPatients();
      return;
    }

    try {
      setIsSearching(true);
      await searchPatients(searchQuery);
    } catch (error) {
      toast({
        title: 'Error searching patients',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handlePatientClick = (patientId: string) => {
    navigate(`/patients/${patientId}`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Text color="red.500">{error}</Text>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Stack spacing={4}>
        <Flex justify="space-between" align="center">
          <InputGroup maxW="400px">
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search patients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </InputGroup>
          <Button
            colorScheme="blue"
            onClick={() => navigate('/patients/new')}
          >
            Register New Patient
          </Button>
        </Flex>

        <Box overflowX="auto">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Phone</Th>
                <Th>County</Th>
                <Th>Status</Th>
                <Th>Registration Date</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {patients.map((patient) => (
                <Tr
                  key={patient.id}
                  _hover={{ bg: 'gray.50', cursor: 'pointer' }}
                  onClick={() => handlePatientClick(patient.id)}
                >
                  <Td>
                    {patient.first_name} {patient.last_name}
                  </Td>
                  <Td>{patient.phone_number}</Td>
                  <Td>{patient.county}</Td>
                  <Td>
                    <Badge colorScheme={statusColors[patient.status]}>
                      {patient.status}
                    </Badge>
                  </Td>
                  <Td>{formatDate(patient.registration_date)}</Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<ChevronDownIcon />}
                        variant="ghost"
                        size="sm"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Actions
                      </MenuButton>
                      <MenuList>
                        <MenuItem onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/patients/${patient.id}/edit`);
                        }}>
                          Edit
                        </MenuItem>
                        <MenuItem onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/patients/${patient.id}/medical-records`);
                        }}>
                          Medical Records
                        </MenuItem>
                        <MenuItem onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/patients/${patient.id}/immunizations`);
                        }}>
                          Immunizations
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </Stack>
    </Box>
  );
}; 