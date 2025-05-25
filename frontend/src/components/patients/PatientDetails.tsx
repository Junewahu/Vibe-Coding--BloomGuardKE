import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Badge,
  Stack,
  Divider,
  Button,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardBody,
  CardHeader,
  List,
  ListItem,
  ListIcon,
  Flex,
  Spinner,
} from '@chakra-ui/react';
import { FiUser, FiPhone, FiMapPin, FiCalendar, FiAlertCircle, FiHeart, FiFileText } from 'react-icons/fi';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatient } from '../../hooks/usePatient';

export const PatientDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    selectedPatient: patient,
    isLoading,
    getPatient,
  } = usePatient();

  useEffect(() => {
    if (id) {
      getPatient(id);
    }
  }, [id, getPatient]);

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (!patient) {
    return (
      <Box textAlign="center" py={10}>
        <Heading size="lg" mb={4}>Patient Not Found</Heading>
        <Button onClick={() => navigate('/patients')}>Back to Patients</Button>
      </Box>
    );
  }

  return (
    <Box>
      <Stack spacing={6}>
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Stack>
            <Heading size="lg">
              {patient.first_name} {patient.last_name}
            </Heading>
            <Text color="gray.500">MRN: {patient.mrn}</Text>
          </Stack>
          <Stack direction="row">
            <Button
              colorScheme="blue"
              onClick={() => navigate(`/patients/${patient.id}/edit`)}
            >
              Edit Patient
            </Button>
          </Stack>
        </Flex>

        {/* Status and Flags */}
        <Stack direction="row" spacing={4}>
          <Badge
            colorScheme={
              patient.status === 'active'
                ? 'green'
                : patient.status === 'inactive'
                ? 'yellow'
                : 'red'
            }
            px={3}
            py={1}
            borderRadius="full"
          >
            {patient.status}
          </Badge>
          {patient.flags.high_risk && (
            <Badge colorScheme="red" px={3} py={1} borderRadius="full">
              High Risk
            </Badge>
          )}
          {patient.flags.special_needs && (
            <Badge colorScheme="purple" px={3} py={1} borderRadius="full">
              Special Needs
            </Badge>
          )}
          {patient.flags.requires_follow_up && (
            <Badge colorScheme="orange" px={3} py={1} borderRadius="full">
              Follow-up Required
            </Badge>
          )}
        </Stack>

        <Divider />

        {/* Main Content */}
        <Tabs>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Medical History</Tab>
            <Tab>Caregivers</Tab>
            <Tab>Documents</Tab>
          </TabList>

          <TabPanels>
            {/* Overview Tab */}
            <TabPanel>
              <Grid templateColumns="repeat(2, 1fr)" gap={6}>
                <Card>
                  <CardHeader>
                    <Heading size="md">Personal Information</Heading>
                  </CardHeader>
                  <CardBody>
                    <List spacing={3}>
                      <ListItem>
                        <ListIcon as={FiUser} />
                        Gender: {patient.gender}
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiCalendar} />
                        Date of Birth: {new Date(patient.date_of_birth).toLocaleDateString()}
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiMapPin} />
                        Address: {`${patient.contact_info.address.street}, ${patient.contact_info.address.city}, ${patient.contact_info.address.county}`}
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiPhone} />
                        Phone: {patient.contact_info.phone}
                      </ListItem>
                      {patient.contact_info.alternative_phone && (
                        <ListItem>
                          <ListIcon as={FiPhone} />
                          Alternative Phone: {patient.contact_info.alternative_phone}
                        </ListItem>
                      )}
                      {patient.contact_info.email && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Email: {patient.contact_info.email}
                        </ListItem>
                      )}
                    </List>
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">Demographics</Heading>
                  </CardHeader>
                  <CardBody>
                    <List spacing={3}>
                      {patient.demographics.ethnicity && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Ethnicity: {patient.demographics.ethnicity}
                        </ListItem>
                      )}
                      <ListItem>
                        <ListIcon as={FiUser} />
                        Language Preference: {patient.demographics.language_preference}
                      </ListItem>
                      {patient.demographics.education_level && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Education Level: {patient.demographics.education_level}
                        </ListItem>
                      )}
                      {patient.demographics.occupation && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Occupation: {patient.demographics.occupation}
                        </ListItem>
                      )}
                      {patient.demographics.insurance_provider && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Insurance Provider: {patient.demographics.insurance_provider}
                        </ListItem>
                      )}
                      {patient.demographics.insurance_number && (
                        <ListItem>
                          <ListIcon as={FiUser} />
                          Insurance Number: {patient.demographics.insurance_number}
                        </ListItem>
                      )}
                    </List>
                  </CardBody>
                </Card>

                {patient.biometrics && (
                  <Card>
                    <CardHeader>
                      <Heading size="md">Biometrics</Heading>
                    </CardHeader>
                    <CardBody>
                      <List spacing={3}>
                        {patient.biometrics.fingerprint_id && (
                          <ListItem>
                            <ListIcon as={FiUser} />
                            Fingerprint ID: {patient.biometrics.fingerprint_id}
                          </ListItem>
                        )}
                        {patient.biometrics.facial_id && (
                          <ListItem>
                            <ListIcon as={FiUser} />
                            Facial ID: {patient.biometrics.facial_id}
                          </ListItem>
                        )}
                        {patient.biometrics.photo_url && (
                          <ListItem>
                            <ListIcon as={FiUser} />
                            Photo: Available
                          </ListItem>
                        )}
                      </List>
                    </CardBody>
                  </Card>
                )}
              </Grid>
            </TabPanel>

            {/* Medical History Tab */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <Heading size="md">Medical History</Heading>
                </CardHeader>
                <CardBody>
                  <Stack spacing={4}>
                    <Box>
                      <Heading size="sm" mb={2}>Chronic Conditions</Heading>
                      <List spacing={2}>
                        {patient.medical_history.chronic_conditions.map((condition, index) => (
                          <ListItem key={index}>
                            <ListIcon as={FiAlertCircle} color="red.500" />
                            {condition}
                          </ListItem>
                        ))}
                      </List>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Allergies</Heading>
                      <List spacing={2}>
                        {patient.medical_history.allergies.map((allergy, index) => (
                          <ListItem key={index}>
                            <ListIcon as={FiAlertCircle} color="orange.500" />
                            {allergy}
                          </ListItem>
                        ))}
                      </List>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Previous Surgeries</Heading>
                      <List spacing={2}>
                        {patient.medical_history.previous_surgeries.map((surgery, index) => (
                          <ListItem key={index}>
                            <ListIcon as={FiFileText} color="blue.500" />
                            {surgery}
                          </ListItem>
                        ))}
                      </List>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Family History</Heading>
                      <List spacing={2}>
                        {patient.medical_history.family_history.map((history, index) => (
                          <ListItem key={index}>
                            <ListIcon as={FiFileText} color="blue.500" />
                            {history}
                          </ListItem>
                        ))}
                      </List>
                    </Box>

                    <Box>
                      <Heading size="sm" mb={2}>Current Medications</Heading>
                      <List spacing={2}>
                        {patient.medical_history.current_medications.map((medication, index) => (
                          <ListItem key={index}>
                            <ListIcon as={FiFileText} color="blue.500" />
                            {medication}
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  </Stack>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Caregivers Tab */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <Heading size="md">Caregivers</Heading>
                </CardHeader>
                <CardBody>
                  <List spacing={4}>
                    {patient.caregivers.map((caregiver) => (
                      <ListItem key={caregiver.id}>
                        <Stack>
                          <Heading size="sm">
                            {caregiver.first_name} {caregiver.last_name}
                          </Heading>
                          <Text>Relationship: {caregiver.relationship}</Text>
                          <Text>Phone: {caregiver.contact_info.phone}</Text>
                          {caregiver.contact_info.email && (
                            <Text>Email: {caregiver.contact_info.email}</Text>
                          )}
                          <Stack direction="row" spacing={2}>
                            <Badge colorScheme="green">
                              {caregiver.engagement.preferred_contact_method}
                            </Badge>
                            <Badge colorScheme="blue">
                              Response Rate: {caregiver.engagement.response_rate}%
                            </Badge>
                          </Stack>
                        </Stack>
                      </ListItem>
                    ))}
                  </List>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Documents Tab */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <Heading size="md">Documents</Heading>
                </CardHeader>
                <CardBody>
                  <Text>Document management coming soon...</Text>
                </CardBody>
              </Card>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Stack>
    </Box>
  );
}; 