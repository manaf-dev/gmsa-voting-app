<script setup lang="ts">
import {
  ArrowLeft,
  Check,
  ArrowBigLeft,
  ChevronsLeft,
  ChevronsRight,
  TriangleAlert,
  User,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  X,
  FileText
} from 'lucide-vue-next'
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { useAuthStore } from '@/stores/authStore'
import BaseBtn from '@/components/BaseBtn.vue'
import ManifestoModal from '@/components/ManifestoModal.vue'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()
const authStore = useAuthStore()
const toast = useToast()

const electionId = route.params.id as string
const currentElection = ref<any>(null)
const positions = ref<any[]>([])
const currentPositionIndex = ref(0)
const votes = ref<Record<string, string | boolean>>({}) // positionId -> candidateId or boolean for yes/no
const loading = ref(false)
const error = ref<string | null>(null)
const showSummary = ref(false)
const hasVoted = ref(false)

// Computed properties
const currentPosition = computed(() => positions.value[currentPositionIndex.value])
const currentCandidates = computed(() => currentPosition.value?.candidates || [])
const totalPositions = computed(() => positions.value.length)
const progress = computed(() => ((currentPositionIndex.value + 1) / totalPositions.value) * 100)
const canProceed = computed(() => {
  if (!currentPosition.value) return false
  return votes.value[currentPosition.value.id] !== undefined
})
const isLastPosition = computed(() => currentPositionIndex.value === totalPositions.value - 1)
const hasSingleCandidate = computed(() => {
  return currentPosition.value?.candidates?.length === 1
})

// Methods
const fetchElectionData = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Fetch election details
    currentElection.value = await electionStore.fetchElectionDetails(electionId)
    
    // Extract positions from election data
    if (currentElection.value?.positions) {
      positions.value = currentElection.value.positions
    } else {
      // Fallback: fetch positions separately if not included
      positions.value = await electionStore.fetchPositions(electionId)
    }
    
    // If user already voted in this election, prevent access
    const votedMap = authStore.user?.active_elections_vote_status || {}
    if (votedMap[electionId]) {
      toast.info('You have already voted in this election.')
      if (currentElection.value?.can_view_results) {
        router.replace(`/elections/${electionId}/results`)
      } else {
        router.replace('/dashboard')
      }
      return
    }

    // Check if election is active; if not but results can be viewed, redirect there
    if (currentElection.value?.status !== 'active') {
      if (currentElection.value?.can_view_results) {
        router.replace(`/elections/${electionId}/results`)
        return
      }
      error.value = 'This election is not currently active.'
      return
    }
    
    // Check if positions exist
    if (positions.value.length === 0) {
      error.value = 'No positions found for this election.'
      return
    }
    
  } catch (err: any) {
    console.error('Error fetching election data:', err)
    error.value = 'Failed to load election data.'
  } finally {
    loading.value = false
  }
}

const selectCandidate = (candidateId: string) => {
  if (!currentPosition.value) return
  votes.value[currentPosition.value.id] = candidateId
}

const selectYesNoVote = (choice: boolean) => {
  if (!currentPosition.value) return
  votes.value[currentPosition.value.id] = choice
}

const nextPosition = () => {
  if (!canProceed.value) return
  
  if (isLastPosition.value) {
    showSummary.value = true
  } else {
    currentPositionIndex.value++
  }
}

const previousPosition = () => {
  if (currentPositionIndex.value > 0) {
    currentPositionIndex.value--
  }
}

const showVoteSummary = () => {
  if (canProceed.value) {
    showSummary.value = true
  }
}

const backToVoting = () => {
  showSummary.value = false
}

const submitVotes = async () => {
  try {
    loading.value = true
    error.value = null

  // Build selections payload. For single-candidate positions, send approve flag (true/false)
  const selections: Array<{ position_id: string; candidate_id?: string; approve?: boolean }> = []

    for (const pos of positions.value) {
      const vote = votes.value[pos.id]
      if (vote === undefined) continue
      if (pos.candidates?.length === 1) {
        if (vote === true) {
          selections.push({ position_id: pos.id, approve: true })
        } else if (vote === false) {
          selections.push({ position_id: pos.id, approve: false })
        }
      } else {
        if (typeof vote === 'string') {
          selections.push({ position_id: pos.id, candidate_id: vote })
        }
      }
    }

    if (selections.length === 0) {
      toast.error('Please make at least one valid selection before submitting.')
      return
    }

    const resp = await electionStore.submitBallot(electionId, selections)
    toast.success('Ballot submitted successfully!')
    hasVoted.value = true

    // Refresh user profile so active_elections_vote_status updates in UI badges
    try {
      const saved = localStorage.getItem('auth_user')
      const prev = saved ? JSON.parse(saved) : null
      const userId = prev?.id
      if (userId) {
        const me = await (await import('@/services/api')).default.get(`/accounts/users/${userId}/retrieve/`)
        authStore.user = me.data
        localStorage.setItem('auth_user', JSON.stringify(authStore.user))
      }
    } catch {}
  } catch (err: any) {
    console.error('Error submitting votes:', err?.response?.data || err)
    toast.error(err?.response?.data?.error || 'Failed to submit votes. Please try again.')
  } finally {
    loading.value = false
  }
}

// Manifesto modal functionality
const selectedManifesto = ref(null)
const showManifestoModal = ref(false)

const openManifestoModal = (candidate: any) => {
  selectedManifesto.value = candidate
  showManifestoModal.value = true
}

const closeManifestoModal = () => {
  showManifestoModal.value = false
  selectedManifesto.value = null
}

const truncateText = (text: string, lines = 2) => {
  if (!text) return ''
  const words = text.split(' ')
  // Estimate roughly 10-12 words per line for mobile
  const wordsPerLine = 10
  const maxWords = lines * wordsPerLine
  if (words.length <= maxWords) return text
  return words.slice(0, maxWords).join(' ') + '...'
}

const goBack = () => {
  router.push('/dashboard')
}

onMounted(() => {
  fetchElectionData()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 w-full">
      <div
        class="max-w-6xl w-full mx-auto px-4 lg:px-8 flex justify-between items-center py-3 md:py-5"
      >
        <div class="flex items-center space-x-4">
          <button @click="goBack" class="text-primary-600">
            <ArrowLeft class="w-5 h-5 text-gray-700" />
          </button>
          <h1 class="text-xl font-semibold text-gray-700">
            Vote - {{ currentElection?.title || 'Election' }}
          </h1>
        </div>
        <div class="text-sm text-gray-600" v-if="!showSummary && !hasVoted">
          <span>Step {{ currentPositionIndex + 1 }} of {{ totalPositions }}</span>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl w-full mx-auto px-4 lg:px-8 py-3 md:py-5">
      <!-- Loading State -->
      <div v-if="loading && !hasVoted" class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-500">Loading election...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <TriangleAlert class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Unable to load voting interface</h3>
        <p class="text-gray-500 mb-4">{{ error }}</p>
        <BaseBtn
          @click="goBack"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          Back to Dashboard
        </BaseBtn>
      </div>

      <!-- Already Voted -->
      <div v-else-if="hasVoted" class="text-center py-12">
        <div
          class="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
        >
          <Check class="w-8 h-8 text-green-600" />
        </div>
        <h2 class="text-2xl font-semibold text-gray-900 mb-2">Vote Submitted Successfully!</h2>
        <p class="text-gray-600 mb-4 text-sm">Thank you for participating in this election.</p>
        <div class="flex item-center gap-2 md:gap-4 w-max mx-auto">
          
          <router-link
            to="/dashboard"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            Back to Home
          </router-link>
        </div>
      </div>

      <!-- Vote Summary -->
      <div v-else-if="showSummary" class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Review Your Votes</h2>
          <p class="text-gray-600 mb-6">Please review your selections before submitting your vote.</p>

          <div class="space-y-4">
            <div
              v-for="position in positions"
              :key="position.id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <h3 class="font-semibold text-gray-900 mb-2">{{ position.title }}</h3>
              
              <div v-if="position.candidates?.length === 1">
                <!-- Yes/No vote -->
                <div class="flex items-center gap-3">
                  <div class="shrink-0">
                    <img
                      v-if="position.candidates[0].profile_picture_url || position.candidates[0].profile_picture"
                      :src="position.candidates[0].profile_picture_url || position.candidates[0].profile_picture"
                      :alt="position.candidates[0].user?.display_name || 'Candidate photo'"
                      loading="lazy"
                      class="w-40 h-40 md:w-48 md:h-48 rounded-full object-cover border border-gray-200 mx-auto md:mx-0"
                    />
                    <div v-else class="w-40 h-40 md:w-48 md:h-48 bg-green-50 rounded-full flex items-center justify-center border border-gray-200 mx-auto md:mx-0">
                      <User class="h-16 w-16 md:h-20 md:w-20 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <p class="font-medium">{{ position.candidates[0].user?.display_name }}</p>
                    <p class="text-sm text-gray-600">
                      Your vote: 
                      <span :class="votes[position.id] === true ? 'text-green-600 font-medium' : 'text-red-600 font-medium'">
                        {{ votes[position.id] === true ? 'YES' : 'NO' }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              <div v-else>
                <!-- Candidate selection -->
                <div v-if="votes[position.id]" class="flex items-center gap-3">
                  <div class="shrink-0">
                    <img
                      v-if="position.candidates?.find((c: any) => c.id === votes[position.id]).profile_picture_url || position.candidates?.find((c: any) => c.id === votes[position.id]).profile_picture"
                      :src="position.candidates?.find((c: any) => c.id === votes[position.id]).profile_picture_url || position.candidates?.find((c: any) => c.id === votes[position.id]).profile_picture"
                      :alt="position.candidates?.find((c: any) => c.id === votes[position.id]).user?.display_name || 'Candidate photo'"
                      loading="lazy"
                      class="w-40 h-40 md:w-48 md:h-48 rounded-full object-cover border border-gray-200 mx-auto md:mx-0"
                    />
                    <div v-else class="w-40 h-40 md:w-48 md:h-48 bg-green-50 rounded-full flex items-center justify-center border border-gray-200 mx-auto md:mx-0">
                      <User class="h-16 w-16 md:h-20 md:w-20 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <p class="font-medium">
                      {{ position.candidates?.find((c: any) => c.id === votes[position.id])?.user?.display_name }}
                    </p>
                    <p class="text-sm text-gray-600">Selected candidate</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex gap-4 mt-6">
            <BaseBtn
              @click="backToVoting"
              class="flex-1 inline-flex items-center justify-center px-4 py-3 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ChevronsLeft class="h-5 w-5 mr-2" />
              Back to Review
            </BaseBtn>
            <BaseBtn
              @click="submitVotes"
              :disabled="loading"
              class="flex-1 inline-flex items-center justify-center px-4 py-3 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
            >
              <span v-if="loading">Submitting...</span>
              <span v-else>Submit Vote</span>
            </BaseBtn>
          </div>
        </div>
      </div>

      <!-- Main Voting Interface -->
      <div v-else-if="positions.length > 0" class="space-y-6">
        <!-- Progress Bar -->
        <div class="bg-white rounded-lg shadow p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">
              {{ currentPosition?.title }}
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-green-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
        </div>

        <!-- Position Content -->
        <div class="bg-white rounded-lg shadow">
          <div class="p-6">
            <div class="text-center mb-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ currentPosition?.title }}</h2>
              <p v-if="currentPosition?.description" class="text-gray-600">
                {{ currentPosition.description }}
              </p>
            </div>

            <!-- Single Candidate - Yes/No Vote -->
            <div v-if="currentCandidates.length === 1" class="space-y-4">
              <div class="border border-gray-200 rounded-lg p-4">
                <div class="flex flex-col md:flex-row items-center md:items-start gap-4 mb-4">
                  <div class="shrink-0">
                    <img
                      v-if="currentCandidates[0].profile_picture_url || currentCandidates[0].profile_picture"
                      :src="currentCandidates[0].profile_picture_url || currentCandidates[0].profile_picture"
                      :alt="currentCandidates[0].user?.display_name || 'Candidate photo'"
                      loading="lazy"
                      class="w-40 h-40 md:w-48 md:h-48 rounded-full object-cover border border-gray-200 mx-auto md:mx-0"
                    />
                    <div v-else class="w-40 h-40 md:w-48 md:h-48 bg-green-50 rounded-full flex items-center justify-center border border-gray-200 mx-auto md:mx-0">
                      <User class="h-16 w-16 md:h-20 md:w-20 text-green-600" />
                    </div>
                  </div>
                  <div class="flex-1 text-center md:text-left w-full">
                    <h3 class="font-semibold text-lg">
                      {{ currentCandidates[0].user?.display_name }}
                    </h3>
                    <!-- <p class="text-gray-600">{{ currentCandidates[0].user?.student_id }}</p> -->
                  </div>
                </div>
                
                <div v-if="currentCandidates[0].manifesto" class="mb-4">
                  <!-- <h4 class="font-medium text-gray-900 mb-2">Manifesto:</h4>
                  <p class="text-gray-600 text-sm manifesto-preview">
                    {{ truncateText(currentCandidates[0].manifesto, 2) }}
                  </p> -->
                  <button
                    @click="openManifestoModal(currentCandidates[0])"
                    class="text-green-600 text-sm font-medium mt-2 flex items-center gap-1 hover:text-green-700"
                  >
                    <FileText class="w-4 h-4" />
                    Read full manifesto
                  </button>
                </div>
              </div>

              <div class="space-y-3">
                <p class="text-center font-medium text-gray-900 mb-4">
                  Do you want to vote for this candidate?
                </p>
                <div class="grid grid-cols-2 gap-4">
                  <button
                    @click="selectYesNoVote(true)"
                    :class="[
                      'p-4 rounded-lg border-2 font-medium transition-all duration-200',
                      votes[currentPosition.id] === true
                        ? 'border-green-500 bg-green-50 text-green-700'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-green-400'
                    ]"
                  >
                    <Check class="w-6 h-6 mx-auto mb-2" />
                    YES
                  </button>
                  <button
                    @click="selectYesNoVote(false)"
                    :class="[
                      'p-4 rounded-lg border-2 font-medium transition-all duration-200',
                      votes[currentPosition.id] === false
                        ? 'border-red-500 bg-red-50 text-red-700'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-red-400'
                    ]"
                  >
                    <X class="w-6 h-6 mx-auto mb-2" />
                    NO
                  </button>
                </div>
              </div>
            </div>

            <!-- Multiple Candidates - Choose One -->
            <div v-else class="space-y-4">
              <p class="text-center font-medium text-gray-900 mb-6">
                Choose one candidate for this position:
              </p>
              
              <div class="grid gap-4 grid-cols-1 sm:grid-cols-2">
                <button
                  v-for="candidate in currentCandidates"
                  :key="candidate.id"
                  @click="selectCandidate(candidate.id)"
                  :class="[
                    'p-4 rounded-lg border-2 text-left transition-all duration-200',
                    votes[currentPosition.id] === candidate.id
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-white hover:border-green-400'
                  ]"
                >
                  <div class="flex flex-col sm:flex-row items-center sm:items-start gap-4">
                    <div class="shrink-0">
                      <img
                        v-if="candidate.profile_picture_url || candidate.profile_picture"
                        :src="candidate.profile_picture_url || candidate.profile_picture"
                        :alt="candidate.user?.display_name || 'Candidate photo'"
                        loading="lazy"
                        class="w-32 h-32 sm:w-36 sm:h-36 md:w-40 md:h-40 rounded-full object-cover border border-gray-200 mx-auto sm:mx-0"
                      />
                      <div v-else class="w-32 h-32 sm:w-36 sm:h-36 md:w-40 md:h-40 bg-green-50 rounded-full flex items-center justify-center border border-gray-200 mx-auto sm:mx-0">
                        <User class="h-14 w-14 sm:h-16 sm:w-16 text-green-600" />
                      </div>
                    </div>
                    <div class="flex-1 text-center sm:text-left w-full">
                      <h3 class="font-semibold text-lg">{{ candidate.user?.display_name }}</h3>
                      <!-- <p class="text-gray-600">{{ candidate.user?.student_id }}</p> -->
                      <div v-if="candidate.manifesto" class="mt-2">
                        <!-- <p class="text-gray-600 text-sm manifesto-preview">
                          {{ truncateText(candidate.manifesto, 2) }}
                        </p> -->
                        <button
                          @click.stop="openManifestoModal(candidate)"
                          class="text-green-600 text-sm font-medium mt-1 flex items-center gap-1 hover:text-green-700"
                        >
                          <FileText class="w-4 h-4" />
                          Read full manifesto
                        </button>
                      </div>
                    </div>
                    <div v-if="votes[currentPosition.id] === candidate.id" class="ml-0 sm:ml-4 mt-2 sm:mt-0">
                      <Check class="w-6 h-6 text-green-600" />
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Navigation Buttons -->
            <div class="flex justify-between mt-8 pt-6 border-t border-gray-200">
              <BaseBtn
                v-if="currentPositionIndex > 0"
                @click="previousPosition"
                class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <ChevronLeft class="h-5 w-5 mr-2" />
                Previous
              </BaseBtn>
              <div v-else></div>

              <BaseBtn
                v-if="currentPositionIndex < totalPositions - 1"
                @click="nextPosition"
                :disabled="!canProceed"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight class="h-5 w-5 ml-2" />
              </BaseBtn>
              <BaseBtn
                v-else
                @click="showVoteSummary"
                :disabled="!canProceed"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Review Votes
                <ArrowRight class="h-5 w-5 ml-2" />
              </BaseBtn>
            </div>
          </div>
        </div>
      </div>

      <!-- No Positions -->
      <div v-else-if="!loading" class="text-center py-12">
        <TriangleAlert class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Positions Available</h3>
        <p class="text-gray-500 mb-4">This election doesn't have any positions to vote for.</p>
        <BaseBtn
          @click="goBack"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          Back to Dashboard
        </BaseBtn>
      </div>
    </div>
  </div>

  <!-- Manifesto Modal -->
  <ManifestoModal
    :show="showManifestoModal"
    :candidate="selectedManifesto"
    @close="closeManifestoModal"
  />
</template>

<style scoped>
.manifesto-preview {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
