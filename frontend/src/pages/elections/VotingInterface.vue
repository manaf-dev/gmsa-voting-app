<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
const isSubmitting = ref(false)
const votes = ref<Record<number, number>>({})
const userVotes = ref<any[]>([])
const currentStep = ref(0)

const hasVoted = computed(() => {
  return userVotes.value.length > 0
})

const totalSteps = computed(() => {
  return election.value?.positions?.length || 0
})

const currentPosition = computed(() => {
  return election.value?.positions?.[currentStep.value]
})

const canProceed = computed(() => {
  if (!currentPosition.value) return false
  return votes.value[currentPosition.value.id] !== undefined
})

const allVotesCast = computed(() => {
  if (!election.value?.positions) return false
  return election.value.positions.every((position: any) => votes.value[position.id] !== undefined)
})

onMounted(async () => {
  if (!authStore.canVote) {
    router.push('/payment/dues')
    return
  }

  isLoading.value = true
  try {
    election.value = await electionsStore.fetchElection(props.id)

    if (election.value.status !== 'active') {
      router.push(`/elections/${props.id}`)
      return
    }

    await electionsStore.fetchUserVotes(props.id)
    userVotes.value = electionsStore.userVotes
  } catch (error) {
    console.error('Failed to load election:', error)
    router.push('/elections')
  } finally {
    isLoading.value = false
  }
})

const selectCandidate = (candidateId: number) => {
  if (!currentPosition.value) return
  votes.value[currentPosition.value.id] = candidateId
}

const nextStep = () => {
  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const submitVotes = async () => {
  if (!allVotesCast.value) return

  isSubmitting.value = true
  try {
    for (const [positionId, candidateId] of Object.entries(votes.value)) {
      await electionsStore.castVote(Number(positionId), candidateId)
    }

    // Redirect to results or confirmation page
    router.push(`/elections/${props.id}/results`)
  } catch (error) {
    console.error('Failed to submit votes:', error)
  } finally {
    isSubmitting.value = false
  }
}

const getSelectedCandidateName = (positionId: number) => {
  const position = election.value?.positions?.find((p: any) => p.id === positionId)
  const candidateId = votes.value[positionId]
  const candidate = position?.candidates?.find((c: any) => c.id === candidateId)
  return candidate?.name || ''
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
            <h1 class="text-xl font-bold text-gray-900">Vote - {{ election?.title }}</h1>
          </div>

          <div class="text-sm text-gray-600">Step {{ currentStep + 1 }} of {{ totalSteps }}</div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
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
        <p class="mt-2 text-sm text-gray-600">Loading voting interface...</p>
      </div>

      <!-- Already Voted -->
      <div v-else-if="hasVoted" class="text-center py-12">
        <div
          class="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
        >
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">You have already voted!</h2>
        <p class="text-gray-600 mb-6">Thank you for participating in this election.</p>
        <div class="space-x-4">
          <router-link :to="`/elections/${id}`" class="btn btn-outline">
            View Election Details
          </router-link>
          <router-link to="/elections" class="btn btn-primary"> Back to Elections </router-link>
        </div>
      </div>

      <!-- Voting Interface -->
      <div v-else-if="election && currentPosition" class="space-y-6">
        <!-- Progress Bar -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Voting Progress</h2>
            <span class="text-sm text-gray-600">{{ currentStep + 1 }}/{{ totalSteps }}</span>
          </div>

          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Current Position -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="mb-6">
            <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ currentPosition.title }}</h3>
            <p v-if="currentPosition.description" class="text-gray-600">
              {{ currentPosition.description }}
            </p>
            <p class="text-sm text-gray-500 mt-2">Select one candidate for this position</p>
          </div>

          <!-- Candidates -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              v-for="candidate in currentPosition.candidates"
              :key="candidate.id"
              @click="selectCandidate(candidate.id)"
              :class="[
                'text-left p-4 border-2 rounded-lg transition-all',
                votes[currentPosition.id] === candidate.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300',
              ]"
            >
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0">
                  <div
                    class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-primary-600 font-medium">
                      {{ candidate.name.charAt(0) }}
                    </span>
                  </div>
                </div>

                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-gray-900">{{ candidate.name }}</h4>
                  <p class="text-sm text-gray-600">{{ candidate.student_id }}</p>
                  <p class="text-xs text-gray-500 mb-2">
                    Level {{ candidate.year_of_study }} | {{ candidate.program }}
                  </p>

                  <div v-if="candidate.manifesto" class="mt-2">
                    <p class="text-sm text-gray-700 line-clamp-3">{{ candidate.manifesto }}</p>
                  </div>
                </div>

                <div v-if="votes[currentPosition.id] === candidate.id" class="flex-shrink-0">
                  <div class="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                    <svg
                      class="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Navigation -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <button v-if="currentStep > 0" @click="prevStep" class="btn btn-outline">
              Previous
            </button>
            <div v-else></div>

            <div class="flex items-center space-x-4">
              <button
                v-if="currentStep < totalSteps - 1"
                @click="nextStep"
                :disabled="!canProceed"
                class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>

              <button
                v-else
                @click="submitVotes"
                :disabled="!allVotesCast || isSubmitting"
                class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <svg
                  v-if="isSubmitting"
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
                {{ isSubmitting ? 'Submitting...' : 'Submit Votes' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Vote Summary -->
        <div v-if="Object.keys(votes).length > 0" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Selections</h3>
          <div class="space-y-2">
            <div
              v-for="position in election.positions"
              :key="position.id"
              class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0"
            >
              <span class="text-sm text-gray-600">{{ position.title }}:</span>
              <span class="text-sm font-medium text-gray-900">
                {{ votes[position.id] ? getSelectedCandidateName(position.id) : 'Not selected' }}
              </span>
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
        <h3 class="text-lg font-medium text-gray-900 mb-2">Unable to load voting interface</h3>
        <p class="text-gray-500 mb-4">
          There was an error loading the election or it may not be active.
        </p>
        <router-link to="/elections" class="btn btn-primary"> Back to Elections </router-link>
      </div>
    </div>
  </div>
</template>
