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
  Badge,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';
import { format, subDays } from 'date-fns';

interface ResponseStats {
  total_reminders: number;
  confirmed: number;
  cancelled: number;
  rescheduled: number;
  no_response: number;
  response_rate: number;
  trend: 'up' | 'down' | 'stable';
}

interface Response {
  id: string;
  reminder_id: string;
  patient_id: string;
  received_at: string;
  action: 'confirmed' | 'cancelled' | 'rescheduled';
  channel: 'sms' | 'whatsapp' | 'voice' | 'ussd';
  notes?: string;
  follow_up_id?: string;
}

export const ResponseTracker: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [isLoading, setIsLoading] = useState(true);
  const [responses, setResponses] = useState<Response[]>([]);
  const [stats, setStats] = useState<ResponseStats>({
    total_reminders: 0,
    confirmed: 0,
    cancelled: 0,
    rescheduled: 0,
    no_response: 0,
    response_rate: 0,
    trend: 'stable',
  });
  const { currentPatient, getPatient } = usePatientStore();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadPatientAndResponses();
  }, [id]);

  const loadPatientAndResponses = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      await getPatient(id);
      // TODO: Implement getResponses in patientStore
      // const responses = await getResponses(id);
      // setResponses(responses);
      // calculateStats(responses);
    } catch (error) {
      toast({
        title: 'Error loading responses',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (responses: Response[]) => {
    const total = responses.length;
    const confirmed = responses.filter(r => r.action === 'confirmed').length;
    const cancelled = responses.filter(r => r.action === 'cancelled').length;
    const rescheduled = responses.filter(r => r.action === 'rescheduled').length;
    const noResponse = stats.total_reminders - total;
    const responseRate = (total / stats.total_reminders) * 100;

    // Calculate trend based on last 7 days vs previous 7 days
    const last7Days = responses.filter(r => 
      new Date(r.received_at) > subDays(new Date(), 7)
    ).length;
    const previous7Days = responses.filter(r => 
      new Date(r.received_at) > subDays(new Date(), 14) && 
      new Date(r.received_at) <= subDays(new Date(), 7)
    ).length;

    const trend = last7Days > previous7Days ? 'up' : 
                 last7Days < previous7Days ? 'down' : 'stable';

    setStats({
      total_reminders: stats.total_reminders,
      confirmed,
      cancelled,
      rescheduled,
      no_response: noResponse,
      response_rate: responseRate,
      trend,
    });
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'confirmed':
        return 'green';
      case 'cancelled':
        return 'red';
      case 'rescheduled':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'sms':
        return 'blue';
      case 'whatsapp':
        return 'green';
      case 'voice':
        return 'purple';
      case 'ussd':
        return 'orange';
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
          <Heading size="lg">Response Tracking</Heading>
          <Button
            colorScheme="red"
            variant="outline"
            onClick={() => navigate(`/patients/${id}`)}
          >
            Back to Patient
          </Button>
        </Flex>

        <Card>
          <CardHeader>
            <Heading size="md">
              {currentPatient.first_name} {currentPatient.last_name}
            </Heading>
          </CardHeader>
          <CardBody>
            <Grid templateColumns="repeat(4, 1fr)" gap={4} mb={6}>
              <GridItem>
                <Stat>
                  <StatLabel>Response Rate</StatLabel>
                  <StatNumber>{stats.response_rate.toFixed(1)}%</StatNumber>
                  <StatHelpText>
                    <StatArrow type={stats.trend} />
                    {stats.trend === 'up' ? 'Increasing' : 
                     stats.trend === 'down' ? 'Decreasing' : 'Stable'}
                  </StatHelpText>
                </Stat>
              </GridItem>
              <GridItem>
                <Stat>
                  <StatLabel>Confirmed</StatLabel>
                  <StatNumber>{stats.confirmed}</StatNumber>
                  <StatHelpText>Total confirmations</StatHelpText>
                </Stat>
              </GridItem>
              <GridItem>
                <Stat>
                  <StatLabel>Cancelled</StatLabel>
                  <StatNumber>{stats.cancelled}</StatNumber>
                  <StatHelpText>Total cancellations</StatHelpText>
                </Stat>
              </GridItem>
              <GridItem>
                <Stat>
                  <StatLabel>No Response</StatLabel>
                  <StatNumber>{stats.no_response}</StatNumber>
                  <StatHelpText>Pending responses</StatHelpText>
                </Stat>
              </GridItem>
            </Grid>

            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Channel</Th>
                  <Th>Action</Th>
                  <Th>Notes</Th>
                </Tr>
              </Thead>
              <Tbody>
                {responses.map((response) => (
                  <Tr key={response.id}>
                    <Td>{format(new Date(response.received_at), 'MMM d, yyyy HH:mm')}</Td>
                    <Td>
                      <Badge colorScheme={getChannelColor(response.channel)}>
                        {response.channel.toUpperCase()}
                      </Badge>
                    </Td>
                    <Td>
                      <Badge colorScheme={getActionColor(response.action)}>
                        {response.action}
                      </Badge>
                    </Td>
                    <Td>{response.notes || '-'}</Td>
                  </Tr>
                ))}
                {responses.length === 0 && (
                  <Tr>
                    <Td colSpan={4} textAlign="center">
                      No responses recorded
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Stack>
    </Box>
  );
}; 