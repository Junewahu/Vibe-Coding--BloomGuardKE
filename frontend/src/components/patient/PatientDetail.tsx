import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Flex,
  Grid,
  GridItem,
  Heading,
  Stack,
  Text,
  useToast,
  Badge,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Spinner,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { Patient, PatientStatus } from '../../types/patient';
import { format } from 'date-fns';

const statusColors: Record<PatientStatus, string> = {
  active: 'green',
  inactive: 'gray',
  deceased: 'red',
  transferred: 'blue',
};

export const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const { currentPatient, getPatient, updatePatient } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadPatient();
  }, [id]);

  const loadPatient = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
    } catch (error) {
      toast({
        title: 'Error loading patient',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: PatientStatus) => {
    if (!currentPatient) return;
    try {
      await updatePatient(currentPatient.id, { status: newStatus });
      toast({
        title: 'Status updated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error updating status',
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
          <Heading size="lg">
            {currentPatient.first_name} {currentPatient.last_name}
          </Heading>
          <Flex gap={2}>
            <Button
              colorScheme="blue"
              onClick={() => navigate(`/patients/${id}/edit`)}
            >
              Edit
            </Button>
            <Button
              colorScheme="red"
              variant="outline"
              onClick={() => navigate('/patients')}
            >
              Back to List
            </Button>
          </Flex>
        </Flex>

        <Card>
          <CardHeader>
            <Flex justify="space-between" align="center">
              <Heading size="md">Patient Information</Heading>
              <Badge colorScheme={statusColors[currentPatient.status]} fontSize="md">
                {currentPatient.status}
              </Badge>
            </Flex>
          </CardHeader>
          <CardBody>
            <Tabs>
              <TabList>
                <Tab>Basic Info</Tab>
                <Tab>Medical Info</Tab>
                <Tab>Caregiver</Tab>
                <Tab>Documents</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                  <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                    <GridItem>
                      <Text fontWeight="bold">NHIF Number</Text>
                      <Text>{currentPatient.nhif_number || 'Not provided'}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Date of Birth</Text>
                      <Text>{format(new Date(currentPatient.date_of_birth), 'PPP')}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Gender</Text>
                      <Text>{currentPatient.gender}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Phone Number</Text>
                      <Text>{currentPatient.phone_number}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Email</Text>
                      <Text>{currentPatient.email || 'Not provided'}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Address</Text>
                      <Text>{currentPatient.address}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">County</Text>
                      <Text>{currentPatient.county}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Sub-county</Text>
                      <Text>{currentPatient.sub_county}</Text>
                    </GridItem>
                  </Grid>
                </TabPanel>

                <TabPanel>
                  <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                    <GridItem>
                      <Text fontWeight="bold">Blood Type</Text>
                      <Text>{currentPatient.blood_type || 'Not provided'}</Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Allergies</Text>
                      <Text>
                        {currentPatient.allergies?.length
                          ? currentPatient.allergies.join(', ')
                          : 'None reported'}
                      </Text>
                    </GridItem>
                    <GridItem>
                      <Text fontWeight="bold">Chronic Conditions</Text>
                      <Text>
                        {currentPatient.chronic_conditions?.length
                          ? currentPatient.chronic_conditions.join(', ')
                          : 'None reported'}
                      </Text>
                    </GridItem>
                  </Grid>
                </TabPanel>

                <TabPanel>
                  {currentPatient.primary_caregiver ? (
                    <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                      <GridItem>
                        <Text fontWeight="bold">Name</Text>
                        <Text>
                          {currentPatient.primary_caregiver.first_name}{' '}
                          {currentPatient.primary_caregiver.last_name}
                        </Text>
                      </GridItem>
                      <GridItem>
                        <Text fontWeight="bold">Relationship</Text>
                        <Text>{currentPatient.primary_caregiver.relationship}</Text>
                      </GridItem>
                      <GridItem>
                        <Text fontWeight="bold">Phone Number</Text>
                        <Text>{currentPatient.primary_caregiver.phone_number}</Text>
                      </GridItem>
                      <GridItem>
                        <Text fontWeight="bold">Email</Text>
                        <Text>
                          {currentPatient.primary_caregiver.email || 'Not provided'}
                        </Text>
                      </GridItem>
                    </Grid>
                  ) : (
                    <Text>No primary caregiver assigned</Text>
                  )}
                </TabPanel>

                <TabPanel>
                  <Stack spacing={4}>
                    <Button
                      colorScheme="blue"
                      onClick={() => navigate(`/patients/${id}/medical-records`)}
                    >
                      View Medical Records
                    </Button>
                    <Button
                      colorScheme="blue"
                      onClick={() => navigate(`/patients/${id}/immunizations`)}
                    >
                      View Immunizations
                    </Button>
                  </Stack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>
      </Stack>
    </Box>
  );
}; 