import { useCallback } from 'react';
import { apiGateway, APIError } from '../services/apiGateway';
import { useToast } from '@chakra-ui/react';

interface UseApiOptions {
  showErrorToast?: boolean;
  errorMessage?: string;
}

export const useApi = (options: UseApiOptions = {}) => {
  const { showErrorToast = true, errorMessage = 'An error occurred' } = options;
  const toast = useToast();

  const handleError = useCallback((error: unknown) => {
    if (error instanceof APIError) {
      if (showErrorToast) {
        toast({
          title: 'Error',
          description: error.message || errorMessage,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
      throw error;
    }
    throw error;
  }, [showErrorToast, errorMessage, toast]);

  const get = useCallback(async <T>(url: string) => {
    try {
      return await apiGateway.get<T>(url);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  const post = useCallback(async <T>(url: string, data?: any) => {
    try {
      return await apiGateway.post<T>(url, data);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  const put = useCallback(async <T>(url: string, data?: any) => {
    try {
      return await apiGateway.put<T>(url, data);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  const patch = useCallback(async <T>(url: string, data?: any) => {
    try {
      return await apiGateway.patch<T>(url, data);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  const del = useCallback(async <T>(url: string) => {
    try {
      return await apiGateway.delete<T>(url);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  const uploadFile = useCallback(async <T>(url: string, formData: FormData) => {
    try {
      return await apiGateway.uploadFile<T>(url, formData);
    } catch (error) {
      return handleError(error);
    }
  }, [handleError]);

  return {
    get,
    post,
    put,
    patch,
    delete: del,
    uploadFile,
  };
}; 