import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { useAuthStore } from '../stores/authStore';

// API Gateway Configuration
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
  },
  PATIENTS: {
    BASE: '/patients',
    SEARCH: '/patients/search',
    MEDICAL_RECORDS: (id: string) => `/patients/${id}/medical-records`,
    IMMUNIZATIONS: (id: string) => `/patients/${id}/immunizations`,
    DOCUMENTS: (id: string) => `/patients/${id}/documents`,
    FOLLOW_UPS: (id: string) => `/patients/${id}/follow-ups`,
    REMINDERS: (id: string) => `/patients/${id}/reminders`,
    RESPONSES: (id: string) => `/patients/${id}/responses`,
    CAREGIVERS: (id: string) => `/patients/${id}/caregivers`,
    ADHERENCE: (id: string) => `/patients/${id}/adherence-metrics`,
    INCENTIVES: (id: string) => `/patients/${id}/incentives`,
  },
  CHW: {
    VISITS: (id: string) => `/chw/${id}/visits`,
    ACTIVITIES: (id: string) => `/chw/${id}/activities`,
  },
};

// Custom error class for API errors
export class APIError extends Error {
  constructor(
    public status: number,
    public message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Extend InternalAxiosRequestConfig to include _retry property
interface ExtendedInternalAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// API Gateway class
class APIGateway {
  private static instance: APIGateway;
  private axiosInstance: AxiosInstance;
  private retryCount: number = 0;

  private constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  public static getInstance(): APIGateway {
    if (!APIGateway.instance) {
      APIGateway.instance = new APIGateway();
    }
    return APIGateway.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.set('Authorization', `Bearer ${token}`);
        }
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as ExtendedInternalAxiosRequestConfig;

        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest?._retry) {
          if (this.retryCount < API_CONFIG.RETRY_ATTEMPTS) {
            this.retryCount++;
            try {
              const refreshToken = useAuthStore.getState().refreshToken;
              const response = await this.axiosInstance.post(API_ENDPOINTS.AUTH.REFRESH, {
                refresh_token: refreshToken,
              });

              const { token } = response.data;
              useAuthStore.getState().setToken(token);

              if (originalRequest) {
                originalRequest._retry = true;
                originalRequest.headers.set('Authorization', `Bearer ${token}`);
                return this.axiosInstance(originalRequest);
              }
            } catch (refreshError) {
              useAuthStore.getState().logout();
              return Promise.reject(refreshError);
            }
          }
        }

        // Handle other errors
        if (error.response) {
          const errorMessage = error.response.data?.message || 'An error occurred';
          throw new APIError(
            error.response.status,
            errorMessage,
            error.response.data
          );
        }

        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  public async get<T>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.get<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async post<T>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async put<T>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async patch<T>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async delete<T>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.delete<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // File upload method
  public async uploadFile<T>(url: string, formData: FormData, config?: InternalAxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.post<T>(url, formData, {
        ...config,
        headers: {
          ...config?.headers,
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handler
  private handleError(error: any): APIError {
    if (error instanceof APIError) {
      return error;
    }

    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.message || error.message;
      return new APIError(
        error.response?.status || 500,
        errorMessage,
        error.response?.data
      );
    }

    return new APIError(500, 'An unexpected error occurred');
  }
}

// Export singleton instance
export const apiGateway = APIGateway.getInstance(); 