<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, Calendar, Users, Clock, User } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useElectionStore } from '@/stores/electionStore'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()
const authStore = useAuthStore()

const electionId = route.params.id as string
const currentElection = ref<any>(null)
const positions = ref<any[]>([])
const loading = ref(false)

const fmt12h = (d?: string | Date) => {
  if (!d) return 'TBA'
  const date = new Date(d)
  const datePart = date.toLocaleDateString()
  const timePart = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
  return `${datePart} ${timePart}`
}

const goBack = () => {
  router.back()
}

const viewPositionDetails = (positionId: string) => {
  router.push(`/voter/elections/${electionId}/positions/${positionId}`)
}

const fetchElectionData = async () => {
  try {
    loading.value = true

    // Fetch election details
    currentElection.value = await electionStore.fetchElectionDetails(electionId)

    // Fetch positions for this election
    positions.value = await electionStore.fetchPositions(electionId)
  } catch (error) {
    console.error('Error fetching election data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchElectionData()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <BaseBtn
          class="flex items-center gap-1 text-gray-700 hover:bg-gray-100 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowLeft />
        </BaseBtn>
        <h1 class="text-xl font-semibold text-gray-700">Election Details</h1>
      </template>
    </NavBar>

    <div v-if="!loading" class="max-w-4xl mx-auto py-4 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <!-- Election Header -->
      <div class="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-6">
        <div class="text-center mb-6">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            {{ currentElection?.title }}
          </h1>
          <p class="text-gray-600 text-base sm:text-lg">{{ currentElection?.description }}</p>
        </div>

        <!-- Voting Action Button for Active Elections -->
        <div v-if="currentElection?.status === 'active'" class="mb-6 text-center">
          <router-link
            :to="`/elections/${electionId}/vote`"
            :class="['inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-medium transition-colors shadow-md', authStore.user?.active_elections_vote_status?.[electionId] ? 'opacity-50 pointer-events-none cursor-not-allowed' : '']"
          >
            🗳️ Cast Your Vote
          </router-link>
        </div>

        <!-- Election Status and Info -->
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-center">
          <div class="flex flex-col items-center">
            <div
              class="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-full flex items-center justify-center mb-2"
            >
              <Calendar class="h-5 w-5 sm:h-6 sm:w-6 text-green-600" />
            </div>
            <span class="text-xs sm:text-sm text-gray-500">Starts</span>
            <span class="font-semibold text-gray-900 text-sm">{{ fmt12h(currentElection?.start_date) }}</span>
          </div>
          <div class="flex flex-col items-center">
            <div
              class="w-10 h-10 sm:w-12 sm:h-12 bg-red-100 rounded-full flex items-center justify-center mb-2"
            >
              <Clock class="h-5 w-5 sm:h-6 sm:w-6 text-red-600" />
            </div>
            <span class="text-xs sm:text-sm text-gray-500">Ends</span>
            <span class="font-semibold text-gray-900 text-sm">{{ fmt12h(currentElection?.end_date) }}</span>
          </div>
          <div class="flex flex-col items-center">
            <div
              class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2"
            >
              <Users class="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
            </div>
            <span class="text-xs sm:text-sm text-gray-500">Positions</span>
            <span class="font-semibold text-gray-900 text-sm">{{ positions.length }}</span>
          </div>
        </div>
      </div>

      <!-- Positions List -->
      <div class="bg-white rounded-xl shadow-lg p-4 sm:p-6">
        <h2 class="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">Election Positions</h2>

        <div v-if="positions.length === 0" class="text-center py-12 text-gray-500">
          <Users class="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No positions available</h3>
          <p class="text-gray-500">Positions will be added soon.</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="position in positions"
            :key="position.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-green-300 transition-all cursor-pointer"
            @click="viewPositionDetails(position.id)"
          >
            <div class="space-y-3">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">{{ position.title }}</h3>
                <p class="text-gray-600 text-sm mt-1">
                  {{ position.description || 'No description provided' }}
                </p>
              </div>

              <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="flex justify-left">
                  <span class="text-gray-500">Candidates: {{ position.candidates?.length || 0 }}</span>
                </div>
              </div>

              <div class="pt-2 border-t border-gray-100">
                <p class="text-xs text-green-600 font-medium">Tap to view candidates</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-else class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <div class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-500">Loading election details...</p>
      </div>
    </div>
  </div>
</template>
