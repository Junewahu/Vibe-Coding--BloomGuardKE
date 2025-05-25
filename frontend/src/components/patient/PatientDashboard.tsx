import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Card,
  CardBody,
  Stack,
  List,
  ListItem,
  ListIcon,
  Badge,
  useColorModeValue,
  Spinner,
  Flex,
} from '@chakra-ui/react';
import { useParams } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format } from 'date-fns';
import { MdCheckCircle, MdWarning, MdInfo } from 'react-icons/md';
import { MedicalRecord, Immunization } from '../../types/patient';

export const PatientDashboard: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [recentRecords, setRecentRecords] = useState<MedicalRecord[]>([]);
  const [upcomingImmunizations, setUpcomingImmunizations] = useState<Immunization[]>([]);
  const { currentPatient, getPatient, getMedicalRecords, getImmunizations } = usePatientStore();
  const bgColor = useColorModeValue('white', 'gray.700');

  useEffect(() => {
    loadDashboardData();
  }, [id]);

  const loadDashboardData = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      const [records, immunizations] = await Promise.all([
        getMedicalRecords(id),
        getImmunizations(id),
      ]);
      
      // Get last 5 medical records
      setRecentRecords(records.slice(0, 5));
      
      // Get upcoming immunizations (scheduled and not completed)
      const upcoming = immunizations.filter(
        imm => imm.status === 'scheduled' && new Date(imm.scheduled_date) > new Date()
      );
      setUpcomingImmunizations(upcoming);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
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
      <Stack spacing={6}>
        <Heading size="lg">
          Dashboard: {currentPatient.first_name} {currentPatient.last_name}
        </Heading>

        {/* Key Metrics */}
        <Grid templateColumns="repeat(4, 1fr)" gap={6}>
          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Stat>
                  <StatLabel>Total Visits</StatLabel>
                  <StatNumber>{recentRecords.length}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    23.36%
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Stat>
                  <StatLabel>Upcoming Immunizations</StatLabel>
                  <StatNumber>{upcomingImmunizations.length}</StatNumber>
                  <StatHelpText>Next due: {upcomingImmunizations[0]?.scheduled_date ? format(new Date(upcomingImmunizations[0].scheduled_date), 'MMM d, yyyy') : 'None'}</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Stat>
                  <StatLabel>Last Visit</StatLabel>
                  <StatNumber>
                    {recentRecords[0] ? format(new Date(recentRecords[0].record_date), 'MMM d') : 'N/A'}
                  </StatNumber>
                  <StatHelpText>Days since last visit</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Stat>
                  <StatLabel>Patient Status</StatLabel>
                  <StatNumber>
                    <Badge colorScheme={currentPatient.status === 'active' ? 'green' : 'red'}>
                      {currentPatient.status}
                    </Badge>
                  </StatNumber>
                  <StatHelpText>Last updated: {format(new Date(currentPatient.last_updated), 'MMM d, yyyy')}</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>

        {/* Recent Activity and Upcoming Events */}
        <Grid templateColumns="repeat(2, 1fr)" gap={6}>
          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Heading size="md" mb={4}>Recent Medical Records</Heading>
                <List spacing={3}>
                  {recentRecords.map((record) => (
                    <ListItem key={record.id}>
                      <ListIcon as={MdInfo} color="blue.500" />
                      <Text as="span" fontWeight="bold">{record.record_type}</Text>
                      <Text as="span" ml={2}>
                        {format(new Date(record.record_date), 'MMM d, yyyy')}
                      </Text>
                      {record.diagnosis && (
                        <Text fontSize="sm" color="gray.500" mt={1}>
                          Diagnosis: {record.diagnosis}
                        </Text>
                      )}
                    </ListItem>
                  ))}
                  {recentRecords.length === 0 && (
                    <Text color="gray.500">No recent medical records</Text>
                  )}
                </List>
              </CardBody>
            </Card>
          </GridItem>

          <GridItem>
            <Card bg={bgColor}>
              <CardBody>
                <Heading size="md" mb={4}>Upcoming Immunizations</Heading>
                <List spacing={3}>
                  {upcomingImmunizations.map((immunization) => (
                    <ListItem key={immunization.id}>
                      <ListIcon as={MdWarning} color="orange.500" />
                      <Text as="span" fontWeight="bold">{immunization.vaccine_name}</Text>
                      <Text as="span" ml={2}>
                        {format(new Date(immunization.scheduled_date), 'MMM d, yyyy')}
                      </Text>
                      <Badge ml={2} colorScheme="blue">Scheduled</Badge>
                    </ListItem>
                  ))}
                  {upcomingImmunizations.length === 0 && (
                    <Text color="gray.500">No upcoming immunizations</Text>
                  )}
                </List>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>
      </Stack>
    </Box>
  );
}; 