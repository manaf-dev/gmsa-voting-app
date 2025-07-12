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

    if (election.value.status !== 'completed') {
      // Only completed elections should show full results
      router.push(`/elections/${props.id}`)
      return
    }
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

const getWinner = (candidates: any[]) => {
  if (!candidates || candidates.length === 0) return null
  return candidates.reduce((prev, current) =>
    prev.vote_count > current.vote_count ? prev : current,
  )
}

const getTotalVotes = (candidates: any[]) => {
  if (!candidates) return 0
  return candidates.reduce((sum, candidate) => sum + (candidate.vote_count || 0), 0)
}

const exportResults = () => {
  // This would implement CSV/PDF export functionality
  console.log('Export results functionality would be implemented here')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link :to="`/elections/${id}`" class="text-primary-600 hover:text-primary-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Election Results</h1>
          </div>

          <button v-if="authStore.isECMember" @click="exportResults" class="btn btn-outline btn-sm">
            Export Results
          </button>
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
        <p class="mt-2 text-sm text-gray-600">Loading results...</p>
      </div>

      <!-- Results -->
      <div v-else-if="election" class="space-y-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-center">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ election.title }}</h1>
            <p class="text-gray-600 mb-4">{{ election.description }}</p>

            <div class="flex justify-center items-center space-x-8 text-sm">
              <div>
                <span class="text-gray-500">Election Period:</span>
                <p class="font-medium">
                  {{ formatDate(election.start_date) }} - {{ formatDate(election.end_date) }}
                </p>
              </div>
              <div>
                <span class="text-gray-500">Total Votes Cast:</span>
                <p class="font-medium">{{ election.total_votes || 0 }}</p>
              </div>
              <div>
                <span class="text-gray-500">Voter Turnout:</span>
                <p class="font-medium">{{ election.total_voters || 0 }} voters</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Results by Position -->
        <div v-if="election.positions?.length" class="space-y-6">
          <div
            v-for="position in election.positions"
            :key="position.id"
            class="bg-white rounded-lg shadow"
          >
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-xl font-semibold text-gray-900">{{ position.title }}</h3>
                  <p v-if="position.description" class="text-sm text-gray-600 mt-1">
                    {{ position.description }}
                  </p>
                </div>
                <div class="text-right text-sm text-gray-500">
                  <p>Total Votes: {{ getTotalVotes(position.candidates) }}</p>
                </div>
              </div>
            </div>

            <div class="p-6">
              <div v-if="position.candidates?.length" class="space-y-4">
                <div
                  v-for="(candidate, index) in position.candidates.sort(
                    (a: any, b: any) => (b.vote_count || 0) - (a.vote_count || 0),
                  )"
                  :key="candidate.id"
                  :class="[
                    'border rounded-lg p-4',
                    index === 0 ? 'border-green-300 bg-green-50' : 'border-gray-200',
                  ]"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                      <div class="flex items-center space-x-3">
                        <div
                          :class="[
                            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                            index === 0 ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600',
                          ]"
                        >
                          {{ index + 1 }}
                        </div>

                        <div
                          class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center"
                        >
                          <span class="text-primary-600 font-medium">
                            {{ candidate.name.charAt(0) }}
                          </span>
                        </div>
                      </div>

                      <div>
                        <h4 class="font-semibold text-gray-900 flex items-center">
                          {{ candidate.name }}
                          <svg
                            v-if="index === 0"
                            class="w-5 h-5 text-green-600 ml-2"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fill-rule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                              clip-rule="evenodd"
                            />
                          </svg>
                        </h4>
                        <p class="text-sm text-gray-600">{{ candidate.student_id }}</p>
                        <p class="text-xs text-gray-500">
                          Level {{ candidate.year_of_study }} | {{ candidate.program }}
                        </p>
                      </div>
                    </div>

                    <div class="text-right">
                      <div class="text-2xl font-bold text-gray-900">
                        {{ candidate.vote_count || 0 }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ (candidate.vote_percentage || 0).toFixed(1) }}%
                      </div>
                    </div>
                  </div>

                  <!-- Vote Percentage Bar -->
                  <div class="mt-4">
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        :class="[
                          'h-2 rounded-full transition-all duration-300',
                          index === 0 ? 'bg-green-600' : 'bg-primary-600',
                        ]"
                        :style="{ width: `${candidate.vote_percentage || 0}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-8">
                <p class="text-gray-500">No candidates for this position</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-blue-600 mb-2">
              {{ election.positions?.length || 0 }}
            </div>
            <div class="text-gray-600">Positions Contested</div>
          </div>

          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-green-600 mb-2">
              {{ election.total_votes || 0 }}
            </div>
            <div class="text-gray-600">Total Votes Cast</div>
          </div>

          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-purple-600 mb-2">
              {{ election.total_voters || 0 }}
            </div>
            <div class="text-gray-600">Voters Participated</div>
          </div>
        </div>

        <!-- Winner Announcement -->
        <div
          v-if="election.positions?.length"
          class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow text-white p-8"
        >
          <div class="text-center">
            <h2 class="text-2xl font-bold mb-6">🎉 Congratulations to Our Winners! 🎉</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="position in election.positions"
                :key="position.id"
                class="bg-white/10 backdrop-blur-sm rounded-lg p-4"
              >
                <h3 class="font-semibold mb-2">{{ position.title }}</h3>
                <div v-if="getWinner(position.candidates)">
                  <p class="text-lg font-bold">{{ getWinner(position.candidates).name }}</p>
                  <p class="text-sm opacity-90">
                    {{ getWinner(position.candidates).vote_count }} votes ({{
                      getWinner(position.candidates).vote_percentage?.toFixed(1)
                    }}%)
                  </p>
                </div>
                <div v-else class="text-sm opacity-75">No winner determined</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-center space-x-4">
          <router-link to="/elections" class="btn btn-outline"> Back to Elections </router-link>
          <router-link to="/dashboard" class="btn btn-primary"> Go to Dashboard </router-link>
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
        <h3 class="text-lg font-medium text-gray-900 mb-2">Results not available</h3>
        <p class="text-gray-500 mb-4">
          The election results are not available or the election hasn't completed yet.
        </p>
        <router-link to="/elections" class="btn btn-primary"> Back to Elections </router-link>
      </div>
    </div>
  </div>
</template>
