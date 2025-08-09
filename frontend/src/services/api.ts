import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = '/choreo-apis/gmsa-voting/backend/v1/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Helper to attach Authorization header for current access token if set
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // If api.defaults.headers.common.Authorization is set by auth store, keep it
  return config
})

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config || {}
    const status = error.response?.status

    // Attempt silent refresh on 401 once
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshResponse = await api.post('/accounts/jwt/refresh/', {})
        const newAccess = (refreshResponse.data as any)?.access
        if (newAccess) {
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccess}`
          originalRequest.headers = {
            ...(originalRequest.headers || {}),
            Authorization: `Bearer ${newAccess}`,
          }
          return api(originalRequest)
        }
      } catch (refreshErr) {
        // fall through to redirect
      }

      // Refresh failed; clear auth header and redirect to login
      delete api.defaults.headers.common['Authorization']
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default api