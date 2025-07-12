<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useElectionsStore } from '@/stores/elections'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const electionsStore = useElectionsStore()

const props = defineProps<{
  id: string
}>()

const election = ref<any>(null)
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    election.value = await electionsStore.fetchElection(props.id)
  } catch (error) {
    console.error('Failed to load election:', error)
    router.push('/elections')
  } finally {
    isLoading.value = false
  }
})

const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'upcoming':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-gray-100 text-gray-800'
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
            <router-link to="/elections" class="text-primary-600 hover:text-primary-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Election Details</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
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
        <p class="mt-2 text-sm text-gray-600">Loading election details...</p>
      </div>

      <!-- Election Details -->
      <div v-else-if="election" class="space-y-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-4">
                <h1 class="text-3xl font-bold text-gray-900">{{ election.title }}</h1>
                <span
                  :class="[
                    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                    getStatusColor(election.status),
                  ]"
                >
                  {{ election.status.charAt(0).toUpperCase() + election.status.slice(1) }}
                </span>
              </div>

              <p class="text-gray-600 mb-6">{{ election.description }}</p>

              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Start Date:</span>
                  <p class="font-medium">{{ formatDate(election.start_date) }}</p>
                </div>
                <div>
                  <span class="text-gray-500">End Date:</span>
                  <p class="font-medium">{{ formatDate(election.end_date) }}</p>
                </div>
                <div>
                  <span class="text-gray-500">Total Positions:</span>
                  <p class="font-medium">{{ election.positions?.length || 0 }}</p>
                </div>
                <div>
                  <span class="text-gray-500">Total Votes:</span>
                  <p class="font-medium">{{ election.total_votes || 0 }}</p>
                </div>
              </div>
            </div>

            <div class="ml-6 flex flex-col space-y-2">
              <button
                v-if="election.status === 'active' && authStore.canVote"
                @click="router.push(`/elections/${election.id}/vote`)"
                class="btn btn-primary"
              >
                Vote Now
              </button>

              <button
                v-if="election.status === 'completed'"
                @click="router.push(`/elections/${election.id}/results`)"
                class="btn btn-outline"
              >
                View Results
              </button>
            </div>
          </div>
        </div>

        <!-- Positions and Candidates -->
        <div v-if="election.positions?.length" class="space-y-6">
          <h2 class="text-2xl font-bold text-gray-900">Positions & Candidates</h2>

          <div
            v-for="position in election.positions"
            :key="position.id"
            class="bg-white rounded-lg shadow"
          >
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">{{ position.title }}</h3>
              <p v-if="position.description" class="text-sm text-gray-600 mt-1">
                {{ position.description }}
              </p>
            </div>

            <div class="p-6">
              <div
                v-if="position.candidates?.length"
                class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                <div
                  v-for="candidate in position.candidates"
                  :key="candidate.id"
                  class="border border-gray-200 rounded-lg p-4"
                >
                  <div class="flex items-center space-x-4 mb-4">
                    <div
                      class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center"
                    >
                      <span class="text-primary-600 font-medium">
                        {{ candidate.name.charAt(0) }}
                      </span>
                    </div>
                    <div>
                      <h4 class="font-semibold text-gray-900">{{ candidate.name }}</h4>
                      <p class="text-sm text-gray-600">{{ candidate.student_id }}</p>
                      <p class="text-xs text-gray-500">
                        Level {{ candidate.year_of_study }} | {{ candidate.program }}
                      </p>
                    </div>
                  </div>

                  <div v-if="candidate.manifesto" class="mt-3">
                    <h5 class="text-sm font-medium text-gray-900 mb-2">Manifesto:</h5>
                    <p class="text-sm text-gray-600 line-clamp-3">{{ candidate.manifesto }}</p>
                  </div>

                  <div
                    v-if="election.status === 'completed'"
                    class="mt-4 pt-3 border-t border-gray-100"
                  >
                    <div class="flex items-center justify-between text-sm">
                      <span class="text-gray-500">Votes:</span>
                      <span class="font-medium"
                        >{{ candidate.vote_count || 0 }} ({{
                          (candidate.vote_percentage || 0).toFixed(1)
                        }}%)</span
                      >
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-8">
                <p class="text-gray-500">No candidates registered for this position yet.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Warning -->
        <div
          v-if="!authStore.canVote && election.status === 'active'"
          class="bg-amber-50 border border-amber-200 rounded-lg p-4"
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
              <h3 class="text-sm font-medium text-amber-800">Payment Required</h3>
              <p class="text-sm text-amber-700 mt-1">
                You need to pay your annual membership dues to vote in this election.
                <router-link to="/payment/dues" class="font-medium underline hover:text-amber-600">
                  Pay now
                </router-link>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
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
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Election not found</h3>
        <p class="text-gray-500 mb-4">
          The election you're looking for doesn't exist or has been removed.
        </p>
        <router-link to="/elections" class="btn btn-primary"> Back to Elections </router-link>
      </div>
    </div>
  </div>
</template>
