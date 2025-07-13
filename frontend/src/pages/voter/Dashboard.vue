<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useElectionsStore } from '@/stores/elections'

const router = useRouter()
const authStore = useAuthStore()
const electionsStore = useElectionsStore()

const isLoading = ref(false)
const stats = ref({
  activeElections: 0,
  totalVotes: 0,
  upcomingElections: 0,
  completedElections: 0,
})

const upcomingElections = computed(() =>
  electionsStore.elections.filter((e) => e.status === 'upcoming').slice(0, 3),
)

const activeElections = computed(() =>
  electionsStore.elections.filter((e) => e.status === 'active'),
)

const recentActivity = ref([
  {
    id: 1,
    type: 'payment',
    message: 'Membership dues paid successfully',
    timestamp: new Date(),
    icon: 'check-circle',
  },
])

onMounted(async () => {
  isLoading.value = true
  try {
    await electionsStore.fetchElections()
    updateStats()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    isLoading.value = false
  }
})

const updateStats = () => {
  const elections = electionsStore.elections
  stats.value = {
    activeElections: elections.filter((e) => e.status === 'active').length,
    totalVotes: elections.reduce((sum, e) => sum + (e.total_votes || 0), 0),
    upcomingElections: elections.filter((e) => e.status === 'upcoming').length,
    completedElections: elections.filter((e) => e.status === 'completed').length,
  }
}

const navigateToElection = (electionId: string) => {
  router.push(`/elections/${electionId}`)
}

const navigateToPayment = () => {
  router.push('/payment/dues')
}

const navigateToProfile = () => {
  router.push('/profile')
}

const logout = async () => {
  await authStore.logout()
  router.push('/')
}

const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

const formatTime = (date: string | Date) => {
  return new Date(date).toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-primary-600">GMSA Dashboard</h1>
          </div>

          <div class="flex items-center space-x-4">
            <router-link
              to="/help"
              class="text-sm text-gray-600 hover:text-gray-900 flex items-center"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Help
            </router-link>

            <div class="flex items-center space-x-2 text-sm text-gray-600">
              <div
                class="w-2 h-2 rounded-full"
                :class="authStore.canVote ? 'bg-green-400' : 'bg-red-400'"
              ></div>
              <span>{{ authStore.canVote ? 'Eligible to vote' : 'Payment required' }}</span>
            </div>

            <div class="relative">
              <button
                @click="navigateToProfile"
                class="flex items-center text-sm text-gray-700 hover:text-gray-900"
              >
                <div
                  class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-2"
                >
                  <span class="text-primary-600 font-medium">
                    {{
                      authStore.user?.first_name?.charAt(0) || authStore.user?.username?.charAt(0)
                    }}
                  </span>
                </div>
                {{ authStore.user?.display_name }}
              </button>
            </div>

            <button @click="logout" class="text-sm text-gray-500 hover:text-gray-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">
          Welcome back, {{ authStore.user?.first_name || authStore.user?.username }}!
        </h2>
        <p class="mt-1 text-sm text-gray-600">
          {{ authStore.user?.year_of_study }} | {{ authStore.user?.program }}
        </p>
      </div>

      <!-- Payment Status Alert -->
      <div
        v-if="!authStore.canVote"
        class="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4"
      >
        <div class="flex">
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd"
            />
          </svg>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-amber-800">Payment Required</h3>
            <p class="text-sm text-amber-700 mt-1">
              You need to pay your annual membership dues to participate in elections.
            </p>
            <div class="mt-3">
              <button @click="navigateToPayment" class="btn btn-outline btn-sm">
                Pay Dues Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <svg
                  class="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Active Elections</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.activeElections }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg
                  class="w-5 h-5 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Upcoming Elections</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.upcomingElections }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg
                  class="w-5 h-5 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Votes Cast</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.totalVotes }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg
                  class="w-5 h-5 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Completed Elections</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.completedElections }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Active Elections -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Active Elections</h3>
          </div>
          <div class="p-6">
            <div v-if="activeElections.length === 0" class="text-center py-8">
              <svg
                class="w-12 h-12 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <p class="text-gray-500">No active elections at the moment</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="election in activeElections"
                :key="election.id"
                class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors cursor-pointer"
                @click="navigateToElection(election.id)"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="font-medium text-gray-900">{{ election.title }}</h4>
                    <p class="text-sm text-gray-500 mt-1">{{ election.description }}</p>
                    <p class="text-xs text-gray-400 mt-2">
                      Ends: {{ formatDate(election.end_date) }} at
                      {{ formatTime(election.end_date) }}
                    </p>
                  </div>
                  <div class="flex items-center">
                    <span
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      Active
                    </span>
                    <svg
                      class="w-5 h-5 text-gray-400 ml-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Elections -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Upcoming Elections</h3>
          </div>
          <div class="p-6">
            <div v-if="upcomingElections.length === 0" class="text-center py-8">
              <svg
                class="w-12 h-12 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p class="text-gray-500">No upcoming elections</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="election in upcomingElections"
                :key="election.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="font-medium text-gray-900">{{ election.title }}</h4>
                    <p class="text-sm text-gray-500 mt-1">{{ election.description }}</p>
                    <p class="text-xs text-gray-400 mt-2">
                      Starts: {{ formatDate(election.start_date) }} at
                      {{ formatTime(election.start_date) }}
                    </p>
                  </div>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    Upcoming
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-8 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <router-link
            to="/elections"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
          >
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
              <svg
                class="w-5 h-5 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900">View Elections</span>
          </router-link>

          <router-link
            to="/profile"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
          >
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <svg
                class="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900">My Profile</span>
          </router-link>

          <router-link
            to="/payment/donation"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
          >
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <svg
                class="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900">Make Donation</span>
          </router-link>

          <button
            v-if="authStore.isECMember"
            @click="router.push('/admin')"
            class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
          >
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <svg
                class="w-5 h-5 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900">Admin Panel</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
