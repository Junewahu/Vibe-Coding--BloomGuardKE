import React from 'react';
import {
  Box,
  Button,
  Flex,
  Text,
  Badge,
  useToast,
  Spinner,
} from '@chakra-ui/react';
import { useOfflineSync } from '../../hooks/useOfflineSync';

export const SyncStatus: React.FC = () => {
  const { isOnline, isInitialized, syncStatus, syncNow } = useOfflineSync();
  const toast = useToast();

  const handleSync = async () => {
    try {
      await syncNow();
      toast({
        title: 'Sync completed',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Sync failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  if (!isInitialized) {
    return (
      <Box p={2}>
        <Flex align="center" gap={2}>
          <Spinner size="sm" />
          <Text>Initializing offline sync...</Text>
        </Flex>
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Flex align="center" justify="space-between">
        <Flex align="center" gap={2}>
          <Badge colorScheme={isOnline ? 'green' : 'red'}>
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
          {syncStatus === 'syncing' && (
            <Flex align="center" gap={2}>
              <Spinner size="sm" />
              <Text>Syncing...</Text>
            </Flex>
          )}
          {syncStatus === 'error' && (
            <Badge colorScheme="red">Sync Error</Badge>
          )}
        </Flex>
        <Button
          size="sm"
          colorScheme="blue"
          onClick={handleSync}
          isDisabled={!isOnline || syncStatus === 'syncing'}
        >
          Sync Now
        </Button>
      </Flex>
    </Box>
  );
}; 