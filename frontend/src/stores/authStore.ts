import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import apiInstance from '@/services/api'
import ChangePassword from '@/pages/auth/ChangePassword.vue'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  const user = ref<any>(JSON.parse(localStorage.getItem('auth_user') || 'null'))
  const token = ref<string | null>(sessionStorage.getItem('auth_access') || null) // store access in-memory only
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value)
  const isECMember = computed(() => user.value?.is_ec_member || false)

  // No token restoration from localStorage; refresh cookie handles session longevity

  async function register(UserDetails: object) {
    loading.value = true
    error.value = null

    try {
      const response = await apiInstance.post('/accounts/register/', UserDetails)
      
      return response.data
    } catch (err: any) {
      error.value = 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(UserDetails: any) {
    loading.value = true
    error.value = null

    try {
      // New JWT login endpoint (sets refresh cookie, returns access)
      const response = await apiInstance.post('/accounts/jwt/login/', UserDetails)
      const access = response.data?.access
      if (access) {
        token.value = access
        apiInstance.defaults.headers.common['Authorization'] = `Bearer ${access}`
  // persist until it expires (sessionStorage, cleared by expiry check)
  sessionStorage.setItem('auth_access', access)
      }

  // Fetch user profile after login using user_id from JWT claims
      try {
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
        const claims = access ? parseJwt(access) : null
        const userId = claims?.user_id || claims?.userId || claims?.uid
        if (userId) {
          const me = await apiInstance.get(`/accounts/users/${userId}/retrieve/`)
          user.value = me.data
          localStorage.setItem('auth_user', JSON.stringify(user.value))
        }
      } catch {
        // ignore
      }

      router.push('/dashboard')
      return response.data
    } catch (err: any) {
      throw err 
    } finally {
      loading.value = false
    }
  }


  async function resetPassword(studentId: string) {
    loading.value = true
    error.value = null
    try {
      const response = await apiInstance.post(
        '/accounts/admin/reset-password/',
        { student_id: studentId } // send as JSON
      )
      return response.data
    } catch (err: any) {
      error.value = 'Password reset failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function changePassword(password: object) {
    loading.value = true
    error.value = null
    try {
      const response = await apiInstance.post(
        '/accounts/password/change/',
        password // send the passed object directly
      )
      // Update local user flag so guard stops redirecting
      try {
        if (user.value) {
          user.value.changed_password = true
          localStorage.setItem('auth_user', JSON.stringify(user.value))
        }
      } catch {}
      return response.data
    } catch (err: any) {
      error.value = 'Password change failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  

  function logout() {
    user.value = null
    token.value = null

    // Clear local storage
    localStorage.removeItem('auth_user')

    // Remove token from API headers
    delete apiInstance.defaults.headers.common['Authorization']
  sessionStorage.removeItem('auth_access')

    // Call backend to clear/blacklist refresh cookie
    apiInstance.post('/accounts/jwt/logout/', {}).catch(() => {})

    router.push('/login')
  }

  return {
    user,
    token,
    isAuthenticated,
    isECMember,
    loading,
    error,
    register,
    login,
    resetPassword,
    changePassword,
    logout,
  }
})
