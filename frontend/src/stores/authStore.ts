import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiInstance from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  const user = ref<any>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)


  async function register(UserDetails: object) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiInstance.post('/accounts/register/', UserDetails)
      router.push('/login') // Redirect after signup
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

      user.value = response.data

      if (response.data.token) {
        token.value = response.data.token
        localStorage.setItem('auth_token', response.data.token)
        apiInstance.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }

      router.push('/dashboard')

      return response.data
    } catch (err: any) {
      error.value = 'Invalid credentials'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    register,
    login,
  }
})
