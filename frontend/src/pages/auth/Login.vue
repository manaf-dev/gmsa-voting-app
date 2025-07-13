<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})

const isLoading = ref(false)
const error = ref('')

const canSubmit = computed(() => {
  return form.value.username.trim() && form.value.password.trim() && !isLoading.value
})

const handleLogin = async () => {
  if (!canSubmit.value) return

  isLoading.value = true
  error.value = ''

  try {
    const result = await authStore.login({
      username: form.value.username,
      password: form.value.password,
    })

    if (result.requiresPayment) {
      // Redirect to payment page
      router.push('/payment/dues')
    } else if (result.success) {
      // Redirect to dashboard
      router.push('/dashboard')
    }
  } catch (err: any) {
    if (err.response?.status === 402) {
      // Payment required - redirect to payment
      router.push('/payment/dues')
    } else {
      error.value = err.message || 'Login failed'
    }
  } finally {
    isLoading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div
    class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <button
          @click="goHome"
          class="mb-6 inline-flex items-center text-primary-600 hover:text-primary-700"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          Back to Home
        </button>

        <div class="mb-4">
          <h1 class="text-3xl font-bold text-primary-600">GMSA</h1>
          <p class="text-sm text-gray-600">Ghana Muslim Students Association</p>
        </div>

        <h2 class="text-2xl font-bold text-gray-900">Sign in to your account</h2>
        <p class="mt-2 text-sm text-gray-600">
          Access the voting system and manage your membership
        </p>
      </div>

      <!-- Login Form -->
      <div class="bg-white rounded-xl shadow-xl p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
              <svg class="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Username Field -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              Username or Student ID
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter your username or student ID"
            />
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter your password"
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="!canSubmit"
            class="w-full btn btn-primary py-3 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              v-if="isLoading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>

        <!-- Register Link -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Don't have an account?
            <button
              @click="goToRegister"
              class="font-medium text-primary-600 hover:text-primary-500"
            >
              Register here
            </button>
          </p>
        </div>

        <!-- Payment Notice -->
        <div class="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div class="flex">
            <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-amber-800">
                <strong>Important:</strong> You must pay your annual dues to access the voting
                system. If you haven't paid, you'll be redirected to complete payment after login.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
