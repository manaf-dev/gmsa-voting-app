<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { paymentService } from '@/services/payments'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const props = defineProps<{
  type?: string
}>()

const paymentType = computed(() => props.type || route.params.type || 'dues')

const form = ref({
  amount: 30.0,
  donor_name: '',
  message: '',
  is_anonymous: true,
})

const isLoading = ref(false)
const error = ref('')
const isProcessing = ref(false)

const isDues = computed(() => paymentType.value === 'dues')
const isDonation = computed(() => paymentType.value === 'donation')

const canSubmit = computed(() => {
  if (isDues.value) {
    return form.value.amount > 0 && !isLoading.value
  }
  return form.value.amount > 0 && !isLoading.value
})

const currentAcademicYear = computed(() => {
  const now = new Date()
  const currentYear = now.getFullYear()
  if (now.getMonth() >= 8) {
    // September = month 8 (0-indexed)
    return `${currentYear}/${currentYear + 1}`
  }
  return `${currentYear - 1}/${currentYear}`
})

onMounted(() => {
  if (isDues.value) {
    form.value.amount = 30.0 // Default dues amount
  } else {
    form.value.amount = 10.0 // Minimum donation
  }
})

const handlePayment = async () => {
  if (!canSubmit.value) return

  isLoading.value = true
  error.value = ''

  try {
    const paymentData: any = {
      payment_type: paymentType.value as 'dues' | 'donation',
      amount: form.value.amount,
      currency: 'GHS',
      metadata: {},
    }

    if (isDonation.value) {
      paymentData.metadata = {
        donor_name: form.value.is_anonymous ? '' : form.value.donor_name,
        message: form.value.message,
        is_anonymous: form.value.is_anonymous,
      }
    } else {
      paymentData.metadata = {
        academic_year: currentAcademicYear.value,
      }
    }

    const response = await paymentService.initiatePayment(paymentData)

    if (response.authorization_url) {
      // Redirect to Paystack
      window.location.href = response.authorization_url
    }
  } catch (err: any) {
    error.value = err.message || 'Payment initialization failed'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/')
  }
}

const goToLogin = () => {
  router.push('/login')
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
          @click="goBack"
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
          {{ authStore.isAuthenticated ? 'Back to Dashboard' : 'Back to Home' }}
        </button>

        <div class="mb-4">
          <h1 class="text-3xl font-bold text-primary-600">GMSA</h1>
          <p class="text-sm text-gray-600">Ghana Muslim Students Association</p>
        </div>

        <h2 class="text-2xl font-bold text-gray-900">
          {{ isDues ? 'Pay Membership Dues' : 'Make a Donation' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          {{
            isDues
              ? `Pay your annual membership dues for ${currentAcademicYear}`
              : 'Support GMSA with your generous donation'
          }}
        </p>
      </div>

      <!-- Payment Form -->
      <div class="bg-white rounded-xl shadow-xl p-8">
        <!-- Payment Type Info -->
        <div v-if="isDues" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex">
            <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800">Membership Dues Payment</h3>
              <p class="text-sm text-blue-700 mt-1">
                Annual membership dues are required to participate in elections and access member
                benefits. Your payment covers the academic year {{ currentAcademicYear }}.
              </p>
            </div>
          </div>
        </div>

        <form @submit.prevent="handlePayment" class="space-y-6">
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

          <!-- Amount Field -->
          <div>
            <label for="amount" class="block text-sm font-medium text-gray-700 mb-2">
              Amount (GHS) *
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500"
                >₵</span
              >
              <input
                id="amount"
                v-model.number="form.amount"
                type="number"
                step="0.01"
                min="1"
                required
                :readonly="isDues"
                class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
                :placeholder="isDues ? '30.00' : '10.00'"
              />
            </div>
            <p v-if="isDues" class="mt-1 text-xs text-gray-500">
              Fixed annual membership dues amount
            </p>
          </div>

          <!-- Donation specific fields -->
          <template v-if="isDonation">
            <div>
              <div class="flex items-center mb-4">
                <input
                  id="is_anonymous"
                  v-model="form.is_anonymous"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="is_anonymous" class="ml-2 block text-sm text-gray-700">
                  Make this donation anonymous
                </label>
              </div>

              <div v-if="!form.is_anonymous">
                <label for="donor_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Donor Name (Optional)
                </label>
                <input
                  id="donor_name"
                  v-model="form.donor_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter your name (optional)"
                />
              </div>
            </div>

            <div>
              <label for="message" class="block text-sm font-medium text-gray-700 mb-2">
                Message (Optional)
              </label>
              <textarea
                id="message"
                v-model="form.message"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Leave a message with your donation..."
              />
            </div>
          </template>

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
            {{ isLoading ? 'Processing...' : `Pay ₵${form.amount.toFixed(2)}` }}
          </button>
        </form>

        <!-- Payment Methods Info -->
        <div class="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Payment Information</h3>
          <div class="flex items-center space-x-4 text-xs text-gray-600">
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                  clip-rule="evenodd"
                />
              </svg>
              Secure payment via Paystack
            </div>
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"
                  clip-rule="evenodd"
                />
              </svg>
              All major cards accepted
            </div>
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M18 8a6 6 0 01-7.743 5.743L10 14l-0.257-0.257A6 6 0 1118 8zM10 2a6 6 0 100 12 6 6 0 000-12zm0 8a2 2 0 100-4 2 2 0 000 4z"
                  clip-rule="evenodd"
                />
              </svg>
              Mobile money supported
            </div>
          </div>
        </div>

        <!-- Not logged in notice -->
        <div
          v-if="!authStore.isAuthenticated"
          class="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg"
        >
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
                You need to be logged in to pay membership dues.
                <button
                  @click="goToLogin"
                  class="font-medium text-amber-900 hover:text-amber-700 underline"
                >
                  Sign in here
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
