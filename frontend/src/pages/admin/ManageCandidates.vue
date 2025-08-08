<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Manage Candidates</h1>
              <p class="mt-1 text-sm text-gray-600">{{ election?.title }}</p>
            </div>
            <router-link
              to="/admin"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                ></path>
              </svg>
              Back to Admin
            </router-link>
          </div>
        </div>

        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>

        <div v-else-if="!election" class="text-center py-12">
          <div class="text-gray-500">Election not found</div>
        </div>

        <div v-else class="p-6">
          <!-- Election Status -->
          <div class="mb-6">
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-500">Status:</span>
              <span
                :class="{
                  'px-2 py-1 text-xs font-medium rounded-full': true,
                  'bg-yellow-100 text-yellow-800': election.status === 'upcoming',
                  'bg-green-100 text-green-800': election.status === 'active',
                  'bg-gray-100 text-gray-800': election.status === 'completed',
                  'bg-red-100 text-red-800': election.status === 'cancelled',
                }"
              >
                {{ election.status.toUpperCase() }}
              </span>
              <span class="text-sm text-gray-500">
                {{ new Date(election.start_date).toLocaleDateString() }} -
                {{ new Date(election.end_date).toLocaleDateString() }}
              </span>
            </div>
          </div>

          <!-- Positions and Candidates -->
          <div class="space-y-8">
            <div
              v-for="position in election.positions"
              :key="position.id"
              class="border border-gray-200 rounded-lg"
            >
              <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-lg font-medium text-gray-900">{{ position.title }}</h3>
                    <p v-if="position.description" class="text-sm text-gray-600 mt-1">
                      {{ position.description }}
                    </p>
                  </div>
                  <button
                    @click="openAddCandidateModal(position)"
                    :disabled="election.status !== 'upcoming'"
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                      ></path>
                    </svg>
                    Add Candidate
                  </button>
                </div>
              </div>

              <div class="p-6">
                <div v-if="position.candidates.length === 0" class="text-center py-8 text-gray-500">
                  No candidates added yet
                </div>
                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div
                    v-for="candidate in position.candidates"
                    :key="candidate.id"
                    class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h4 class="font-medium text-gray-900">{{ candidate.name }}</h4>
                        <p class="text-sm text-gray-600">{{ candidate.student_id }}</p>
                        <p class="text-sm text-gray-600">{{ candidate.program }}</p>
                        <p class="text-sm text-gray-600">Year {{ candidate.year_of_study }}</p>
                        <p
                          v-if="candidate.manifesto"
                          class="text-sm text-gray-700 mt-2 line-clamp-3"
                        >
                          {{ candidate.manifesto }}
                        </p>
                      </div>
                      <button
                        v-if="election.status === 'upcoming'"
                        @click="removeCandidate(position.id, candidate.id)"
                        class="ml-2 text-red-600 hover:text-red-800"
                      >
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          ></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Candidate Modal -->
    <div
      v-if="showAddCandidateModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            Add Candidate for {{ selectedPosition?.title }}
          </h3>

          <form @submit.prevent="addCandidate" class="space-y-4">
            <div>
              <label for="candidate-name" class="block text-sm font-medium text-gray-700"
                >Full Name</label
              >
              <input
                type="text"
                id="candidate-name"
                v-model="candidateForm.name"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label for="candidate-student-id" class="block text-sm font-medium text-gray-700"
                >Student ID</label
              >
              <input
                type="text"
                id="candidate-student-id"
                v-model="candidateForm.student_id"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label for="candidate-program" class="block text-sm font-medium text-gray-700"
                >Program</label
              >
              <input
                type="text"
                id="candidate-program"
                v-model="candidateForm.program"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label for="candidate-year" class="block text-sm font-medium text-gray-700"
                >Year of Study</label
              >
              <select
                id="candidate-year"
                v-model="candidateForm.year_of_study"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">Select Year</option>
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">5th Year</option>
                <option value="6">6th Year</option>
              </select>
            </div>

            <div>
              <label for="candidate-manifesto" class="block text-sm font-medium text-gray-700"
                >Manifesto</label
              >
              <textarea
                id="candidate-manifesto"
                v-model="candidateForm.manifesto"
                rows="4"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="Candidate's manifesto and vision..."
              ></textarea>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeAddCandidateModal"
                class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                {{ submitting ? 'Adding...' : 'Add Candidate' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

interface Candidate {
  id: number
  name: string
  student_id: string
  year_of_study: string
  program: string
  manifesto: string
  profile_picture?: string
}

interface Position {
  id: number
  title: string
  description: string
  candidates: Candidate[]
}

interface Election {
  id: string
  title: string
  description: string
  start_date: string
  end_date: string
  status: 'upcoming' | 'active' | 'completed' | 'cancelled'
  positions: Position[]
}

interface CandidateForm {
  name: string
  student_id: string
  year_of_study: string
  program: string
  manifesto: string
}

const route = useRoute()
const electionId = route.params.id as string

const election = ref<Election | null>(null)
const loading = ref(false)
const showAddCandidateModal = ref(false)
const selectedPosition = ref<Position | null>(null)
const submitting = ref(false)

const candidateForm = reactive<CandidateForm>({
  name: '',
  student_id: '',
  year_of_study: '',
  program: '',
  manifesto: '',
})

const fetchElection = async () => {
  loading.value = true
  try {
    const response = await api.get(`/elections/${electionId}/`)
    election.value = response.data
  } catch (error: any) {
    console.error('Error fetching election:', error)
    alert('Failed to load election details')
  } finally {
    loading.value = false
  }
}

const openAddCandidateModal = (position: Position) => {
  selectedPosition.value = position
  showAddCandidateModal.value = true
  resetCandidateForm()
}

const closeAddCandidateModal = () => {
  showAddCandidateModal.value = false
  selectedPosition.value = null
  resetCandidateForm()
}

const resetCandidateForm = () => {
  candidateForm.name = ''
  candidateForm.student_id = ''
  candidateForm.year_of_study = ''
  candidateForm.program = ''
  candidateForm.manifesto = ''
}

const addCandidate = async () => {
  if (!selectedPosition.value) return

  submitting.value = true
  try {
    const response = await api.post(
      `/elections/positions/${selectedPosition.value.id}/candidates/`,
      candidateForm,
    )

    // Add the new candidate to the local state
    selectedPosition.value.candidates.push(response.data)

    closeAddCandidateModal()
    alert('Candidate added successfully!')
  } catch (error: any) {
    console.error('Error adding candidate:', error)
    alert(error.response?.data?.message || 'Failed to add candidate')
  } finally {
    submitting.value = false
  }
}

const removeCandidate = async (positionId: number, candidateId: number) => {
  if (!confirm('Are you sure you want to remove this candidate?')) return

  try {
    await api.delete(`/elections/positions/${positionId}/candidates/${candidateId}/`)

    // Remove candidate from local state
    const position = election.value?.positions.find((p) => p.id === positionId)
    if (position) {
      const index = position.candidates.findIndex((c) => c.id === candidateId)
      if (index > -1) {
        position.candidates.splice(index, 1)
      }
    }

    alert('Candidate removed successfully!')
  } catch (error: any) {
    console.error('Error removing candidate:', error)
    alert(error.response?.data?.message || 'Failed to remove candidate')
  }
}

onMounted(() => {
  fetchElection()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
