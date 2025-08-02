<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { paymentService } from '@/services/payments'

interface Payment {
  id: string
  payment_type: string
  amount: number
  status: string
  paystack_reference: string
  created_at: string
}

interface PaymentStats {
  totalPaid: number
  lastPayment: { date: string } | null
  paymentHistory: Payment[]
}

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const isEditing = ref(false)
const payments = ref<Payment[]>([])
const paymentStats = ref<PaymentStats>({
  totalPaid: 0,
  lastPayment: null,
  paymentHistory: [],
})

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  program: '',
  year_of_study: '',
})

const yearChoices = [
  { value: '100', label: 'Level 100' },
  { value: '200', label: 'Level 200' },
  { value: '300', label: 'Level 300' },
  { value: '400', label: 'Level 400' },
]

onMounted(async () => {
  if (authStore.user) {
    // Initialize form with user data
    form.value = {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      email: authStore.user.email || '',
      phone_number: authStore.user.phone_number || '',
      program: authStore.user.program || '',
      year_of_study: authStore.user.year_of_study || '',
    }
  }

  await loadPaymentHistory()
})

const loadPaymentHistory = async () => {
  try {
    const response = await paymentService.getUserPayments()
    payments.value = response.payments || []
    paymentStats.value = response.stats || {}
  } catch (error) {
    console.error('Failed to load payment history:', error)
  }
}

const updateProfile = async () => {
  isLoading.value = true
  try {
    await authStore.updateProfile(form.value)
    isEditing.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    isLoading.value = false
  }
}

const cancelEdit = () => {
  if (authStore.user) {
    form.value = {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      email: authStore.user.email || '',
      phone_number: authStore.user.phone_number || '',
      program: authStore.user.program || '',
      year_of_study: authStore.user.year_of_study || '',
    }
  }
  isEditing.value = false
}

const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

const formatAmount = (amount: number) => {
  return `₵${amount.toFixed(2)}`
}

const getPaymentStatusColor = (status: string) => {
  switch (status) {
    case 'successful':
      return 'bg-green-100 text-green-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-primary-600 hover:text-primary-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Profile</h1>
          </div>

          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ authStore.user?.display_name }}</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Profile Information -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Profile Information</h3>
              <button v-if="!isEditing" @click="isEditing = true" class="btn btn-outline btn-sm">
                Edit Profile
              </button>
            </div>

            <div class="p-6">
              <div v-if="!isEditing" class="space-y-6">
                <!-- Profile Picture Placeholder -->
                <div class="flex items-center space-x-6">
                  <div
                    class="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-2xl font-bold text-primary-600">
                      {{
                        authStore.user?.first_name?.charAt(0) || authStore.user?.username?.charAt(0)
                      }}
                    </span>
                  </div>
                  <div>
                    <h2 class="text-xl font-bold text-gray-900">
                      {{ authStore.user?.display_name }}
                    </h2>
                    <p class="text-sm text-gray-600">{{ authStore.user?.student_id }}</p>
                    <p class="text-sm text-gray-600">{{ authStore.user?.email }}</p>
                  </div>
                </div>

                <!-- Profile Details -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">First Name</label>
                    <p class="mt-1 text-sm text-gray-900">
                      {{ authStore.user?.first_name || 'Not provided' }}
                    </p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">Last Name</label>
                    <p class="mt-1 text-sm text-gray-900">
                      {{ authStore.user?.last_name || 'Not provided' }}
                    </p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                    <p class="mt-1 text-sm text-gray-900">
                      {{ authStore.user?.phone_number || 'Not provided' }}
                    </p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">Year of Study</label>
                    <p class="mt-1 text-sm text-gray-900">
                      Level {{ authStore.user?.year_of_study || 'Not provided' }}
                    </p>
                  </div>

                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700">Program</label>
                    <p class="mt-1 text-sm text-gray-900">
                      {{ authStore.user?.program || 'Not provided' }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Edit Form -->
              <form v-else @submit.prevent="updateProfile" class="space-y-6">
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
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>

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
                    <label for="program" class="block text-sm font-medium text-gray-700 mb-2">
                      Program *
                    </label>
                    <input
                      id="program"
                      v-model="form.program"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>

                <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
                  <button type="button" @click="cancelEdit" class="btn btn-outline">Cancel</button>
                  <button
                    type="submit"
                    :disabled="isLoading"
                    class="btn btn-primary flex items-center"
                  >
                    <svg
                      v-if="isLoading"
                      class="animate-spin -ml-1 mr-3 h-4 w-4"
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
                    {{ isLoading ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Account Status -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Account Status</h3>

            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Membership Status</span>
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    authStore.canVote ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                  ]"
                >
                  {{ authStore.canVote ? 'Active' : 'Inactive' }}
                </span>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Dues Payment</span>
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    authStore.user?.has_paid_dues
                      ? 'bg-green-100 text-green-800'
                      : 'bg-amber-100 text-amber-800',
                  ]"
                >
                  {{ authStore.user?.has_paid_dues ? 'Paid' : 'Pending' }}
                </span>
              </div>

              <div v-if="authStore.isECMember" class="flex items-center justify-between">
                <span class="text-sm text-gray-600">EC Member</span>
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                >
                  Yes
                </span>
              </div>
            </div>

            <div v-if="!authStore.canVote" class="mt-4 pt-4 border-t border-gray-200">
              <router-link to="/payment/dues" class="btn btn-primary btn-sm w-full">
                Pay Dues Now
              </router-link>
            </div>
          </div>

          <!-- Payment Summary -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Payment Summary</h3>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Total Paid</span>
                <span class="text-sm font-medium text-gray-900">
                  {{ formatAmount(paymentStats.totalPaid) }}
                </span>
              </div>

              <div v-if="paymentStats.lastPayment" class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Last Payment</span>
                <span class="text-sm font-medium text-gray-900">
                  {{ formatDate(paymentStats.lastPayment.date) }}
                </span>
              </div>
            </div>

            <div class="mt-4 pt-4 border-t border-gray-200">
              <router-link to="/payment/donation" class="btn btn-outline btn-sm w-full">
                Make Donation
              </router-link>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>

            <div class="space-y-3">
              <router-link to="/elections" class="block w-full btn btn-outline btn-sm">
                View Elections
              </router-link>

              <router-link to="/dashboard" class="block w-full btn btn-outline btn-sm">
                Dashboard
              </router-link>

              <button
                v-if="authStore.isECMember"
                @click="router.push('/admin')"
                class="block w-full btn btn-outline btn-sm"
              >
                Admin Panel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment History -->
      <div v-if="payments.length > 0" class="mt-8 bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Payment History</h3>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Date
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Type
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Amount
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Reference
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="payment in payments" :key="payment.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(payment.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ payment.payment_type === 'dues' ? 'Membership Dues' : 'Donation' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatAmount(payment.amount) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getPaymentStatusColor(payment.status),
                    ]"
                  >
                    {{ payment.status.charAt(0).toUpperCase() + payment.status.slice(1) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ payment.paystack_reference }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
