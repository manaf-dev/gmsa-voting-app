<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: '',
  student_id: '',
  phone_number: '',
  year_of_study: '',
  program: '',
  admission_year: new Date().getFullYear(),
})

const isLoading = ref(false)
const error = ref('')

const yearChoices = [
  { value: '100', label: 'Level 100' },
  { value: '200', label: 'Level 200' },
  { value: '300', label: 'Level 300' },
  { value: '400', label: 'Level 400' },
]

const canSubmit = computed(() => {
  return (
    form.value.username.trim() &&
    form.value.email.trim() &&
    form.value.password.trim() &&
    form.value.confirmPassword.trim() &&
    form.value.first_name.trim() &&
    form.value.last_name.trim() &&
    form.value.student_id.trim() &&
    form.value.year_of_study &&
    form.value.program.trim() &&
    form.value.password === form.value.confirmPassword &&
    !isLoading.value
  )
})

const passwordsMatch = computed(() => {
  return form.value.password === form.value.confirmPassword || !form.value.confirmPassword
})

const handleRegister = async () => {
  if (!canSubmit.value) return

  isLoading.value = true
  error.value = ''

  try {
    const result = await authStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      confirm_password: form.value.confirmPassword,
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      student_id: form.value.student_id,
      phone_number: form.value.phone_number,
      year_of_study: form.value.year_of_study,
      program: form.value.program,
      admission_year: form.value.admission_year,
    })

    if (result.success) {
      // Registration successful, redirect to payment
      router.push('/payment/dues')
    }
  } catch (err: any) {
    error.value = err.message || 'Registration failed'
  } finally {
    isLoading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div
    class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
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

        <h2 class="text-2xl font-bold text-gray-900">Create your account</h2>
        <p class="mt-2 text-sm text-gray-600">Join GMSA and participate in elections</p>
      </div>

      <!-- Registration Form -->
      <div class="bg-white rounded-xl shadow-xl p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
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

          <!-- Personal Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                First Name *
              </label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="First name"
              />
            </div>

            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
                Last Name *
              </label>
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Last name"
              />
            </div>
          </div>

          <!-- Account Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                Username *
              </label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                autocomplete="username"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Choose a username"
              />
            </div>

            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                autocomplete="email"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="your.email@example.com"
              />
            </div>
          </div>

          <!-- Student Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="student_id" class="block text-sm font-medium text-gray-700 mb-2">
                Student ID *
              </label>
              <input
                id="student_id"
                v-model="form.student_id"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., 12345678"
              />
            </div>

            <div>
              <label for="phone_number" class="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                id="phone_number"
                v-model="form.phone_number"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., +233 20 123 4567"
              />
            </div>
          </div>

          <!-- Academic Information -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label for="year_of_study" class="block text-sm font-medium text-gray-700 mb-2">
                Year of Study *
              </label>
              <select
                id="year_of_study"
                v-model="form.year_of_study"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Select year</option>
                <option v-for="year in yearChoices" :key="year.value" :value="year.value">
                  {{ year.label }}
                </option>
              </select>
            </div>

            <div>
              <label for="admission_year" class="block text-sm font-medium text-gray-700 mb-2">
                Admission Year *
              </label>
              <input
                id="admission_year"
                v-model.number="form.admission_year"
                type="number"
                :min="2020"
                :max="new Date().getFullYear()"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="2024"
              />
            </div>

            <div class="md:col-span-1">
              <label for="program" class="block text-sm font-medium text-gray-700 mb-2">
                Program of Study *
              </label>
              <input
                id="program"
                v-model="form.program"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., Computer Science"
              />
            </div>
          </div>

          <!-- Password Fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                autocomplete="new-password"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Create a strong password"
              />
            </div>

            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password *
              </label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                required
                autocomplete="new-password"
                :class="[
                  'w-full px-3 py-2 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2',
                  passwordsMatch
                    ? 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
                    : 'border-red-300 focus:ring-red-500 focus:border-red-500',
                ]"
                placeholder="Confirm your password"
              />
              <p v-if="!passwordsMatch" class="mt-1 text-sm text-red-600">Passwords do not match</p>
            </div>
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
            {{ isLoading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Already have an account?
            <button @click="goToLogin" class="font-medium text-primary-600 hover:text-primary-500">
              Sign in here
            </button>
          </p>
        </div>

        <!-- Notice -->
        <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex">
            <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-blue-800">
                After registration, you'll need to pay your annual membership dues to access the
                voting system and participate in elections.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
