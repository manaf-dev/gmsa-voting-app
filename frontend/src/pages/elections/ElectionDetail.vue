<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowBigLeft } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { ref, onMounted } from 'vue'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()

// Local state for the election
const election = ref<any | null>(null)

const goBack = () => {
  router.back()
}

const fetchElection = async () => {
  try {
    const id = route.params.id as string // Grab ID from URL
    const data = await electionStore.fetchElectionDetails(id)
    election.value = data
    console.log('Fetched election:', data)
  } catch (error) {
    console.error('Failed to fetch election:', error)
  }
}

onMounted(() => {
  fetchElection()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <BaseBtn
          class="flex items-center gap-1 text-blue-300 hover:bg-blue-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowBigLeft />
        </BaseBtn>
        <h1 class="text-xl font-semibold text-gray-700">Election Details</h1>
      </template>
    </NavBar>

    <div v-if="election" class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <div class="flex flex-col-reverse sm:flex-row sm:items-center gap-4 justify-between">
        <h1 class="text-3xl font-bold text-gray-900">{{ election.title }}</h1>
        <div class="flex items-center gap-4">
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-gray-200 border-2 text-gray-700 px-4 py-2 rounded-lg cursor-pointer"
          >
            Add Position
          </BaseBtn>
          <BaseBtn
            class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
          >
            Cast Vote
          </BaseBtn>
        </div>
      </div>
      <p class="text-gray-600 mb-6">{{ election.description }}</p>

      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm shadow-lg p-6 mb-6 rounded-xl"
      >
        <div>
          <span class="text-gray-500">Start Date:</span>
          <p class="font-medium">{{ new Date(election.start_date).toLocaleString() }}</p>
        </div>
        <div>
          <span class="text-gray-500">End Date:</span>
          <p class="font-medium">{{ new Date(election.end_date).toLocaleString() }}</p>
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

      <!-- Positions & Candidates -->
      <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 shadow-lg rounded-xl">
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center space-x-4 mb-4">
            <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
              <span class="text-primary-600 font-medium">A</span>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">Ahmed Ali</h4>
              <p class="text-sm text-gray-600">5211040227</p>
              <p class="text-xs text-gray-500">Level 300 | Computer Science</p>
            </div>
          </div>

          <div class="mt-3">
            <h5 class="text-sm font-medium text-gray-900 mb-2">Manifesto:</h5>
            <p class="text-sm text-gray-600 line-clamp-3">
              I aim to improve the welfare of GMSA members, enhance collaboration with other
              organizations, and promote educational excellence.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
