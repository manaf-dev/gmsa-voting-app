import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiInstance from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  const user = ref<any>(JSON.parse(localStorage.getItem('auth_user') || 'null'))
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Restore Authorization header if token exists
  if (token.value) {
    apiInstance.defaults.headers.common['Authorization'] = `Token ${token.value}`
  }

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
      const response = await apiInstance.post('/accounts/login/', UserDetails)

      // Save user and token
      user.value = response.data.user
      token.value = response.data.token

      localStorage.setItem('auth_user', JSON.stringify(response.data.user))
      localStorage.setItem('auth_token', response.data.token)

      // Set Authorization header
      apiInstance.defaults.headers['Authorization'] = `Token ${response.data.token}`

      router.push('/dashboard')
      return response.data
    } catch (err: any) {
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
    localStorage.removeItem('auth_token')

    // Remove token from API headers
    delete apiInstance.defaults.headers.common['Authorization']

    router.push('/login')
  }

  return {
    user,
    token,
    loading,
    error,
    register,
    login,
    logout,
  }
})
