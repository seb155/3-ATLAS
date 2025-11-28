import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { useLogStore } from '../store/useLogStore';

/**
 * Setup axios interceptors to handle authentication errors globally
 * This ensures that if a token expires, the user is automatically logged out
 * and redirected to the login screen
 */
export const setupAxiosInterceptors = () => {
  // Request interceptor to add Auth token and Project ID
  axios.interceptors.request.use(
    (config) => {
      const { token } = useAuthStore.getState();
      const { currentProject } = useProjectStore.getState();
      const { addLog } = useLogStore.getState(); // Import dynamically to avoid cycles if any

      // Add Authorization header if token exists
      if (token && !config.url?.includes('/auth/login')) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add Project ID header if project is selected
      if (currentProject) {
        config.headers['X-Project-ID'] = currentProject.id;
      }

      // Log Network Request
      addLog({
        level: 'INFO',
        source: 'NETWORK',
        message: `[REQ] ${config.method?.toUpperCase()} ${config.url}`,
        context: {
          headers: config.headers,
          data: config.data,
          params: config.params
        }
      });

      return config;
    },
    (error) => {
      const { addLog } = useLogStore.getState();
      addLog({
        level: 'ERROR',
        source: 'NETWORK',
        message: `[REQ ERROR] ${error.message}`,
        context: error
      });
      return Promise.reject(error);
    }
  );

  // Response interceptor to catch 401 errors
  axios.interceptors.response.use(
    (response) => {
      const { addLog } = useLogStore.getState();

      // Log Network Response
      addLog({
        level: 'INFO',
        source: 'NETWORK',
        message: `[RES] ${response.status} ${response.config.url}`,
        context: {
          status: response.status,
          data: response.data
        }
      });

      return response;
    },
    (error) => {
      const { addLog } = useLogStore.getState();

      // Log Network Error
      addLog({
        level: 'ERROR',
        source: 'NETWORK',
        message: `[RES ERROR] ${error.response?.status || 'ERR'} ${error.config?.url || 'Unknown URL'} - ${error.message}`,
        context: {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        }
      });

      // Check if the error is a 401 (Unauthorized)
      if (error.response && error.response.status === 401) {
        console.warn('⚠️ 401 Unauthorized - Token expired or invalid. Logging out...');
        const { logout } = useAuthStore.getState();
        logout();
      }

      return Promise.reject(error);
    }
  );

  console.log('✅ Axios interceptors configured - Auto-headers, Auto-logout & Network Logging enabled');
};
