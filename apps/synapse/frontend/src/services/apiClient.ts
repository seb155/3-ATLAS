import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { useLogStore } from '../store/useLogStore';

// Development-only logger - no output in production
const devLog = {
  info: (message: string, ...args: unknown[]) => {
    if (import.meta.env.DEV) {
      console.log(`[API] ${message}`, ...args);
    }
  },
  warn: (message: string, ...args: unknown[]) => {
    if (import.meta.env.DEV) {
      console.warn(`[API] ${message}`, ...args);
    }
  },
  error: (message: string, ...args: unknown[]) => {
    // Always log errors, even in production
    console.error(`[API] ${message}`, ...args);
  },
};

// Create a dedicated Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1', // All requests relative to /api/v1 (goes through proxy)
  timeout: 30000, // 30s timeout
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { token } = useAuthStore.getState();
    const { currentProject } = useProjectStore.getState();
    const { addLog } = useLogStore.getState();

    // If data is FormData, ensure Content-Type is unset so browser sets boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    // Add Authorization header
    if (token && !config.url?.includes('/auth/login')) {
      config.headers.Authorization = `Bearer ${token}`;
      devLog.info('Attaching Bearer token to request:', config.url);
    } else {
      devLog.warn('No token found or login request. URL:', config.url, 'Token exists:', !!token);
    }

    // Add Project ID header
    if (currentProject) {
      config.headers['X-Project-ID'] = currentProject.id;
      devLog.info('Attaching Project ID:', currentProject.id);
    } else {
      devLog.warn('No current project selected.');
    }

    // Log Request to DevConsole
    addLog({
      level: 'INFO',
      source: 'NETWORK',
      message: `[REQ] ${config.method?.toUpperCase()} ${config.url}`,
      context: {
        headers: config.headers,
        params: config.params,
        data: config.data ? '(payload)' : undefined,
      },
    });

    return config;
  },
  (error) => {
    const { addLog } = useLogStore.getState();
    addLog({
      level: 'ERROR',
      source: 'NETWORK',
      message: `[REQ ERROR] ${error.message}`,
      context: error,
    });
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    const { addLog } = useLogStore.getState();

    addLog({
      level: 'INFO',
      source: 'NETWORK',
      message: `[RES] ${response.status} ${response.config.url}`,
      context: {
        status: response.status,
        data: '(response data)',
      },
    });

    return response;
  },
  (error: AxiosError) => {
    const { addLog } = useLogStore.getState();

    addLog({
      level: 'ERROR',
      source: 'NETWORK',
      message: `[RES ERROR] ${error.response?.status || 'ERR'} ${error.config?.url || 'Unknown URL'} - ${error.message}`,
      context: {
        status: error.response?.status,
        data: error.response?.data,
      },
    });

    // Handle 401 Unauthorized (Auto-logout)
    if (error.response?.status === 401) {
      devLog.warn('401 Unauthorized - Token expired or invalid. Logging out...');
      useAuthStore.getState().logout();
      useProjectStore.getState().clearProject();
    }

    return Promise.reject(error);
  }
);

export default apiClient;
