<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-900">Create New Election</h1>
          <p class="mt-1 text-sm text-gray-600">Set up a new election for GMSA members</p>
        </div>

        <form @submit.prevent="createElection" class="p-6 space-y-6">
          <!-- Basic Election Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="title" class="block text-sm font-medium text-gray-700"
                >Election Title</label
              >
              <input
                type="text"
                id="title"
                v-model="electionForm.title"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="e.g., GMSA Executive Elections 2025/2026"
              />
            </div>

            <div>
              <label for="academic_year" class="block text-sm font-medium text-gray-700"
                >Academic Year</label
              >
              <input
                type="text"
                id="academic_year"
                v-model="electionForm.academic_year"
                required
                pattern="\d{4}/\d{4}"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="2025/2026"
              />
            </div>
          </div>

          <div>
            <label for="description" class="block text-sm font-medium text-gray-700"
              >Description</label
            >
            <textarea
              id="description"
              v-model="electionForm.description"
              rows="3"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              placeholder="Brief description of the election..."
            ></textarea>
          </div>

          <!-- Election Dates -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="start_date" class="block text-sm font-medium text-gray-700"
                >Start Date & Time</label
              >
              <input
                type="datetime-local"
                id="start_date"
                v-model="electionForm.start_date"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label for="end_date" class="block text-sm font-medium text-gray-700"
                >End Date & Time</label
              >
              <input
                type="datetime-local"
                id="end_date"
                v-model="electionForm.end_date"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <!-- Positions -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <label class="block text-sm font-medium text-gray-700">Election Positions</label>
              <button
                type="button"
                @click="addPosition"
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                  ></path>
                </svg>
                Add Position
              </button>
            </div>

            <div v-if="electionForm.positions.length === 0" class="text-center py-8 text-gray-500">
              No positions added yet. Click "Add Position" to get started.
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(position, index) in electionForm.positions"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label
                      :for="`position-title-${index}`"
                      class="block text-sm font-medium text-gray-700"
                      >Position Title</label
                    >
                    <input
                      type="text"
                      :id="`position-title-${index}`"
                      v-model="position.title"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                      placeholder="e.g., President, Vice President"
                    />
                  </div>

                  <div>
                    <label
                      :for="`position-max-votes-${index}`"
                      class="block text-sm font-medium text-gray-700"
                      >Max Votes per Voter</label
                    >
                    <input
                      type="number"
                      :id="`position-max-votes-${index}`"
                      v-model.number="position.max_votes_per_voter"
                      min="1"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                    />
                  </div>

                  <div class="flex items-end">
                    <button
                      type="button"
                      @click="removePosition(index)"
                      class="w-full inline-flex justify-center items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      <svg
                        class="h-4 w-4 mr-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        ></path>
                      </svg>
                      Remove
                    </button>
                  </div>
                </div>

                <div class="mt-3">
                  <label
                    :for="`position-description-${index}`"
                    class="block text-sm font-medium text-gray-700"
                    >Description</label
                  >
                  <textarea
                    :id="`position-description-${index}`"
                    v-model="position.description"
                    rows="2"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                    placeholder="Brief description of the position..."
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <router-link
              to="/admin"
              class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Cancel
            </router-link>
            <button
              type="submit"
              :disabled="loading || electionForm.positions.length === 0"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                v-if="loading"
                class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
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
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {{ loading ? 'Creating...' : 'Create Election' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useElectionsStore } from '../../stores/elections'

interface Position {
  title: string
  description: string
  max_votes_per_voter: number
}

interface ElectionForm {
  title: string
  description: string
  academic_year: string
  start_date: string
  end_date: string
  positions: Position[]
}

const router = useRouter()
const electionsStore = useElectionsStore()

const loading = ref(false)
const electionForm = reactive<ElectionForm>({
  title: '',
  description: '',
  academic_year: '',
  start_date: '',
  end_date: '',
  positions: [],
})

const addPosition = () => {
  electionForm.positions.push({
    title: '',
    description: '',
    max_votes_per_voter: 1,
  })
}

const removePosition = (index: number) => {
  electionForm.positions.splice(index, 1)
}

const createElection = async () => {
  if (electionForm.positions.length === 0) {
    alert('Please add at least one position for the election.')
    return
  }

  if (new Date(electionForm.end_date) <= new Date(electionForm.start_date)) {
    alert('End date must be after start date.')
    return
  }

  loading.value = true

  try {
    // Create the election
    const electionData = {
      title: electionForm.title,
      description: electionForm.description,
      academic_year: electionForm.academic_year,
      start_date: electionForm.start_date,
      end_date: electionForm.end_date,
      positions: electionForm.positions,
    }

    await electionsStore.createElection(electionData)

    // Redirect to admin dashboard with success message
    router.push('/admin?created=true')
  } catch (error: any) {
    console.error('Error creating election:', error)
    alert(error.response?.data?.message || 'Failed to create election. Please try again.')
  } finally {
    loading.value = false
  }
}

// Set default academic year
const currentYear = new Date().getFullYear()
const nextYear = currentYear + 1
electionForm.academic_year = `${currentYear}/${nextYear}`
</script>
