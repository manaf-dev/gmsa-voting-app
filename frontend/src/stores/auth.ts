import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  student_id: string
  phone_number: string
  year_of_study: string
  program: string
  has_paid_dues: boolean
  dues_payment_date: string | null
  is_ec_member: boolean
  display_name: string
  can_vote: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isECMember = computed(() => user.value?.is_ec_member || false)
  const canVote = computed(() => user.value?.can_vote || false)

  const setAuthData = (userData: User, authToken: string) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem('auth_token', authToken)
    api.defaults.headers.common['Authorization'] = `Token ${authToken}`
  }

  const clearAuthData = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    delete api.defaults.headers.common['Authorization']
  }

  const checkAuthState = async () => {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
      api.defaults.headers.common['Authorization'] = `Token ${savedToken}`
      try {
        await fetchUserProfile()
      } catch (error) {
        clearAuthData()
      }
    }
  }

  const login = async (credentials: { username: string; password: string }) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/accounts/login/', credentials)
      
      if (response.data.payment_required) {
        error.value = response.data.error
        return { requiresPayment: true, userId: response.data.user_id }
      }
      
      setAuthData(response.data.user, response.data.token)
      return { success: true }
    } catch (err: any) {
      if (err.response?.status === 402) {
        error.value = err.response.data.error
        return { 
          requiresPayment: true, 
          userId: err.response.data.user_id,
          error: err.response.data.error 
        }
      }
      error.value = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/accounts/register/', userData)
      setAuthData(response.data.user, response.data.token)
      return { success: true }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await api.post('/accounts/logout/')
    } catch (error) {
      // Ignore logout errors
    } finally {
      clearAuthData()
    }
  }

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/accounts/profile/')
      user.value = response.data.user
    } catch (error) {
      clearAuthData()
      throw error
    }
  }

  const updateProfile = async (profileData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.put('/accounts/profile/update/', profileData)
      user.value = response.data.user
      return { success: true }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Profile update failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    isECMember,
    canVote,
    login,
    register,
    logout,
    checkAuthState,
    fetchUserProfile,
    updateProfile,
    clearAuthData
  }
})