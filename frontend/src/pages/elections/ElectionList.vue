<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useElectionsStore } from '@/stores/elections'

const router = useRouter()
const authStore = useAuthStore()
const electionsStore = useElectionsStore()

const isLoading = ref(false)
const selectedTab = ref('active')

const tabs = [
  { id: 'active', name: 'Active', count: 0 },
  { id: 'upcoming', name: 'Upcoming', count: 0 },
  { id: 'completed', name: 'Completed', count: 0 },
]

const filteredElections = computed(() => {
  return electionsStore.elections.filter((election) => {
    switch (selectedTab.value) {
      case 'active':
        return election.status === 'active'
      case 'upcoming':
        return election.status === 'upcoming'
      case 'completed':
        return election.status === 'completed'
      default:
        return true
    }
  })
})

const updateTabCounts = () => {
  tabs[0].count = electionsStore.elections.filter((e) => e.status === 'active').length
  tabs[1].count = electionsStore.elections.filter((e) => e.status === 'upcoming').length
  tabs[2].count = electionsStore.elections.filter((e) => e.status === 'completed').length
}

onMounted(async () => {
  isLoading.value = true
  try {
    await electionsStore.fetchElections()
    updateTabCounts()
  } catch (error) {
    console.error('Failed to load elections:', error)
  } finally {
    isLoading.value = false
  }
})

const navigateToElection = (electionId: string) => {
  router.push(`/elections/${electionId}`)
}

const canVoteInElection = (election: any) => {
  return authStore.canVote && election.status === 'active'
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'upcoming':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-gray-100 text-gray-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
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

const getDaysUntil = (date: string | Date) => {
  const now = new Date()
  const targetDate = new Date(date)
  const diffTime = targetDate.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
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
            <h1 class="text-xl font-bold text-gray-900">Elections</h1>
          </div>

          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ authStore.user?.display_name }}</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">GMSA Elections</h2>
            <p class="mt-1 text-sm text-gray-600">
              Participate in democratic elections and make your voice heard
            </p>
          </div>

          <!-- Admin Actions -->
          <div v-if="authStore.isECMember" class="flex items-center space-x-3">
            <router-link
              to="/admin/elections/create"
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                ></path>
              </svg>
              Create Election
            </router-link>
            <router-link
              to="/admin"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Admin Dashboard
            </router-link>
          </div>
        </div>
      </div>

      <!-- Payment Warning -->
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
            <h3 class="text-sm font-medium text-amber-800">Payment Required to Vote</h3>
            <p class="text-sm text-amber-700 mt-1">
              You must pay your annual membership dues to participate in elections.
              <router-link to="/payment/dues" class="font-medium underline hover:text-amber-600">
                Pay now
              </router-link>
            </p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="selectedTab = tab.id"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              selectedTab === tab.id
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            ]"
          >
            {{ tab.name }}
            <span
              :class="[
                'ml-2 py-0.5 px-2 rounded-full text-xs',
                selectedTab === tab.id
                  ? 'bg-primary-100 text-primary-600'
                  : 'bg-gray-100 text-gray-500',
              ]"
            >
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <svg class="animate-spin h-8 w-8 text-primary-600 mx-auto" fill="none" viewBox="0 0 24 24">
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
        <p class="mt-2 text-sm text-gray-600">Loading elections...</p>
      </div>

      <!-- Elections List -->
      <div v-else-if="filteredElections.length > 0" class="grid grid-cols-1 gap-6">
        <div
          v-for="election in filteredElections"
          :key="election.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
          @click="navigateToElection(election.id)"
        >
          <div class="p-6">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-semibold text-gray-900">{{ election.title }}</h3>
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getStatusColor(election.status),
                    ]"
                  >
                    {{ election.status.charAt(0).toUpperCase() + election.status.slice(1) }}
                  </span>
                </div>

                <p class="text-gray-600 mb-4">{{ election.description }}</p>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span class="text-gray-500">Start Date:</span>
                    <p class="font-medium">{{ formatDate(election.start_date) }}</p>
                    <p class="text-xs text-gray-400">{{ formatTime(election.start_date) }}</p>
                  </div>

                  <div>
                    <span class="text-gray-500">End Date:</span>
                    <p class="font-medium">{{ formatDate(election.end_date) }}</p>
                    <p class="text-xs text-gray-400">{{ formatTime(election.end_date) }}</p>
                  </div>

                  <div v-if="election.total_votes !== undefined">
                    <span class="text-gray-500">Total Votes:</span>
                    <p class="font-medium">{{ election.total_votes || 0 }}</p>
                  </div>

                  <div v-if="election.status === 'upcoming'">
                    <span class="text-gray-500">Starts in:</span>
                    <p class="font-medium">
                      {{ getDaysUntil(election.start_date) }} day{{
                        getDaysUntil(election.start_date) !== 1 ? 's' : ''
                      }}
                    </p>
                  </div>

                  <div v-if="election.status === 'active'">
                    <span class="text-gray-500">Ends in:</span>
                    <p class="font-medium">
                      {{ getDaysUntil(election.end_date) }} day{{
                        getDaysUntil(election.end_date) !== 1 ? 's' : ''
                      }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="ml-6 flex items-center">
                <svg
                  class="w-5 h-5 text-gray-400"
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

            <!-- Quick Actions -->
            <div class="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>{{ election.positions?.length || 0 }} positions</span>
                <span>•</span>
                <span>Created by {{ election.created_by_name || 'EC' }}</span>
              </div>

              <div class="flex items-center space-x-2">
                <!-- Admin Actions for EC Members -->
                <div v-if="authStore.isECMember" class="flex items-center space-x-2 mr-2">
                  <router-link
                    :to="`/admin/elections/${election.id}/candidates`"
                    class="text-purple-600 hover:text-purple-800 text-sm font-medium"
                    @click.stop
                  >
                    Manage Candidates
                  </router-link>
                  <span class="text-gray-300">•</span>
                </div>

                <!-- Regular Actions -->
                <button
                  v-if="canVoteInElection(election)"
                  @click.stop="router.push(`/elections/${election.id}/vote`)"
                  class="btn btn-primary btn-sm"
                >
                  Vote Now
                </button>

                <button
                  v-if="election.status === 'completed'"
                  @click.stop="router.push(`/elections/${election.id}/results`)"
                  class="btn btn-outline btn-sm"
                >
                  View Results
                </button>

                <button
                  @click.stop="router.push(`/elections/${election.id}`)"
                  class="btn btn-outline btn-sm"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg
          class="w-16 h-16 text-gray-400 mx-auto mb-4"
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
        <h3 class="text-lg font-medium text-gray-900 mb-2">No {{ selectedTab }} elections</h3>
        <p class="text-gray-500">
          {{
            selectedTab === 'active'
              ? 'There are no active elections at the moment.'
              : selectedTab === 'upcoming'
                ? 'No elections are scheduled for the future.'
                : 'No elections have been completed yet.'
          }}
        </p>

        <div class="mt-6">
          <router-link to="/dashboard" class="btn btn-outline"> Back to Dashboard </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
