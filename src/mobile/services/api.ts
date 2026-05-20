/**
 * MAESTRO API client.
 *
 * Base HTTP client with JWT auth header injection.
 * All requests go through /api/v1/ (IC-12 contract Section 14.1).
 * Response envelope: { data, meta } per IC-12 Section 14.2.
 *
 * No PII is logged or stored in non-secure storage.
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { getTokens } from './auth';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Inject JWT token into every request
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const tokens = await getTokens();
    if (tokens?.accessToken) {
      config.headers.Authorization = `Bearer ${tokens.accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Handle 401 responses (token expired)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token refresh is handled by useAuth hook.
      // Reject so the hook can retry after refresh.
    }
    return Promise.reject(error);
  },
);

export default apiClient;
