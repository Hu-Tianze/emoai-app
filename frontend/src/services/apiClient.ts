import { API_BASE_URL, API_TIMEOUT } from '~/constants/api';
import type { ApiResponse } from '~/types';

async function fetchWithTimeout(
  resource: RequestInfo,
  options: RequestInit & { timeout?: number },
) {
  const { timeout = API_TIMEOUT } = options;

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  let response;
  try {
    response = await fetch(resource, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(id);
  }
}

export const apiClient = {
  async get<T>(path: string): Promise<ApiResponse<T>> {
    const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },

  async post<T>(path: string, data: unknown): Promise<ApiResponse<T>> {
    const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
};
