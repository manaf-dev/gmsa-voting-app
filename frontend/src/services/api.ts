import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Helper to attach Authorization header for current access token if set
apiInstance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // If api.defaults.headers.common.Authorization is set by auth store, keep it
  return config
})

// Response interceptor to handle auth errors
apiInstance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config || {}
    const status = error.response?.status

    // Attempt silent refresh on 401 once
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshResponse = await apiInstance.post('/accounts/jwt/refresh/', {})
        const newAccess = (refreshResponse.data as any)?.access
        if (newAccess) {
          apiInstance.defaults.headers.common['Authorization'] = `Bearer ${newAccess}`
          originalRequest.headers = {
            ...(originalRequest.headers || {}),
            Authorization: `Bearer ${newAccess}`,
          }
          return apiInstance(originalRequest)
        }
      } catch (refreshErr) {
        // fall through to redirect
      }

      // Refresh failed; clear auth header and redirect to login
      delete apiInstance.defaults.headers.common['Authorization']
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default apiInstance