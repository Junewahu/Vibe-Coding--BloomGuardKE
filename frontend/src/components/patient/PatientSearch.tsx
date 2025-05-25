import React, { useState, useEffect } from 'react';
import {
  Box,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  Card,
  CardBody,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Flex,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Select,
  Grid,
  GridItem,
  Badge,
  Text,
  Spinner,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format } from 'date-fns';
import { Patient } from '../../types/patient';

interface SearchFilters {
  status: string;
  county: string;
  gender: string;
  ageRange: string;
  bloodType: string;
}

export const PatientSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    status: '',
    county: '',
    gender: '',
    ageRange: '',
    bloodType: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { patients, searchPatients, getPatients } = usePatientStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setIsLoading(true);
    try {
      await getPatients();
    } catch (error) {
      console.error('Error loading patients:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      await searchPatients(searchQuery);
    } catch (error) {
      console.error('Error searching patients:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (field: keyof SearchFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const applyFilters = (patients: Patient[]) => {
    return patients.filter(patient => {
      if (filters.status && patient.status !== filters.status) return false;
      if (filters.county && patient.county !== filters.county) return false;
      if (filters.gender && patient.gender !== filters.gender) return false;
      if (filters.bloodType && patient.blood_type !== filters.bloodType) return false;
      if (filters.ageRange) {
        const age = calculateAge(patient.date_of_birth);
        const [min, max] = filters.ageRange.split('-').map(Number);
        if (age < min || age > max) return false;
      }
      return true;
    });
  };

  const calculateAge = (dateOfBirth: string) => {
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const filteredPatients = applyFilters(patients);

  return (
    <Box p={4}>
      <Stack spacing={4}>
        <Flex gap={4}>
          <InputGroup>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search patients by name, ID, or phone number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </InputGroup>
          <Button colorScheme="blue" onClick={handleSearch}>
            Search
          </Button>
          <Button onClick={onOpen}>Advanced Filters</Button>
        </Flex>

        <Card>
          <CardBody>
            {isLoading ? (
              <Flex justify="center" align="center" h="200px">
                <Spinner size="xl" />
              </Flex>
            ) : (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>ID</Th>
                    <Th>Phone</Th>
                    <Th>County</Th>
                    <Th>Status</Th>
                    <Th>Last Updated</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {filteredPatients.map((patient) => (
                    <Tr key={patient.id}>
                      <Td>
                        {patient.first_name} {patient.last_name}
                      </Td>
                      <Td>{patient.id}</Td>
                      <Td>{patient.phone_number}</Td>
                      <Td>{patient.county}</Td>
                      <Td>
                        <Badge
                          colorScheme={
                            patient.status === 'active' ? 'green' : 'red'
                          }
                        >
                          {patient.status}
                        </Badge>
                      </Td>
                      <Td>
                        {format(new Date(patient.last_updated), 'MMM d, yyyy')}
                      </Td>
                      <Td>
                        <Button
                          size="sm"
                          colorScheme="blue"
                          onClick={() => navigate(`/patients/${patient.id}`)}
                        >
                          View Details
                        </Button>
                      </Td>
                    </Tr>
                  ))}
                  {filteredPatients.length === 0 && (
                    <Tr>
                      <Td colSpan={7} textAlign="center">
                        <Text color="gray.500">No patients found</Text>
                      </Td>
                    </Tr>
                  )}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>
      </Stack>

      {/* Advanced Filters Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Advanced Filters</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Grid templateColumns="repeat(2, 1fr)" gap={4}>
              <GridItem>
                <FormControl>
                  <FormLabel>Status</FormLabel>
                  <Select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                  >
                    <option value="">All</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="deceased">Deceased</option>
                    <option value="transferred">Transferred</option>
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel>County</FormLabel>
                  <Select
                    value={filters.county}
                    onChange={(e) => handleFilterChange('county', e.target.value)}
                  >
                    <option value="">All</option>
                    <option value="nairobi">Nairobi</option>
                    <option value="mombasa">Mombasa</option>
                    <option value="kisumu">Kisumu</option>
                    {/* Add more counties */}
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel>Gender</FormLabel>
                  <Select
                    value={filters.gender}
                    onChange={(e) => handleFilterChange('gender', e.target.value)}
                  >
                    <option value="">All</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel>Age Range</FormLabel>
                  <Select
                    value={filters.ageRange}
                    onChange={(e) => handleFilterChange('ageRange', e.target.value)}
                  >
                    <option value="">All</option>
                    <option value="0-12">0-12 years</option>
                    <option value="13-18">13-18 years</option>
                    <option value="19-30">19-30 years</option>
                    <option value="31-50">31-50 years</option>
                    <option value="51-100">51+ years</option>
                  </Select>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel>Blood Type</FormLabel>
                  <Select
                    value={filters.bloodType}
                    onChange={(e) => handleFilterChange('bloodType', e.target.value)}
                  >
                    <option value="">All</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </Select>
                </FormControl>
              </GridItem>
            </Grid>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 