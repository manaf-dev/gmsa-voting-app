import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Helper: parse JWT to get exp
const parseJwt = (t: string) => {
  try {
    const base64Url = t.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

// On startup: load access token from sessionStorage if still valid
(() => {
  const saved = sessionStorage.getItem('auth_access')
  if (saved) {
    const claims = parseJwt(saved)
    const nowSec = Math.floor(Date.now() / 1000)
    const exp = claims?.exp as number | undefined
    if (exp && exp > nowSec) {
      apiInstance.defaults.headers.common['Authorization'] = `Bearer ${saved}`
    } else {
      sessionStorage.removeItem('auth_access')
    }
  }
})()

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
      // persist the new access until it expires
      sessionStorage.setItem('auth_access', newAccess)
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
    sessionStorage.removeItem('auth_access')
    localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default apiInstance