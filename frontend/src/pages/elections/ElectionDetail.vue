<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, Edit, Users, Trash2 } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { ref, onMounted, computed } from 'vue'
import CreatePosition from '@/modules/CreatePosition.vue'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()

const showCreatePositionModal = ref(false)
const showEditPositionModal = ref(false)
const editingPosition = ref(null)
const electionId = route.params.id as string

const election = ref<any>(null)
const positions = computed(() => {
  // Use positions from the election response if available, otherwise from electionPositions
  return election.value?.positions || electionStore.electionPositions || []
})

const goBack = () => {
  router.back()
}

const goToPosition = (positionId: string) => {
  router.push(`/elections/${electionId}/positions/${positionId}`).catch((err) => {
    // Optionally handle navigation errors here
    console.error('Navigation error:', err)
  })
}

const editPosition = (position: any) => {
  editingPosition.value = position
  showEditPositionModal.value = true
}

const deletePosition = async (positionId: string) => {
  if (!confirm('Are you sure you want to delete this position? This will also delete all candidates for this position.')) return
  
  try {
    await electionStore.deletePosition(positionId)
    // Refresh positions to update the UI
    await fetchElectionAndPositions()
  } catch (error) {
    console.error('Failed to delete position:', error)
  }
}

const fetchElectionAndPositions = async () => {
  election.value = await electionStore.fetchElectionDetails(electionId)
}

onMounted(() => {
  fetchElectionAndPositions()
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

    <div v-if="election" class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <!-- Header -->
      <div class="flex flex-col-reverse sm:flex-row sm:items-center gap-4 justify-between">
        <h1 class="text-3xl font-bold text-gray-900">{{ election?.title }}</h1>
        <div class="flex items-center gap-4">
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-inherit hover:bg-green-50 border-2 text-green-700 px-4 py-2 rounded-lg cursor-pointer"
            @click="showCreatePositionModal = true"
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

      <p class="text-gray-600 mb-6">{{ election?.description }}</p>

      <!-- Stats -->
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm shadow-lg p-6 mb-6 rounded-xl"
      >
        <div>
          <span class="text-gray-500">Start Date:</span>
          <p class="font-medium">{{ new Date(election?.start_date).toLocaleString() }}</p>
        </div>
        <div>
          <span class="text-gray-500">End Date:</span>
          <p class="font-medium">{{ new Date(election?.end_date).toLocaleString() }}</p>
        </div>
        <div>
          <span class="text-gray-500">Total Positions:</span>
          <p class="font-medium">{{ positions.length }}</p>
        </div>
        <div>
          <span class="text-gray-500">Total Votes:</span>
          <p class="font-medium">{{ election?.total_votes || 0 }}</p>
        </div>
      </div>

      <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 shadow-lg rounded-xl">
        <div
          v-for="position in positions"
          :key="position.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer group"
          @click="goToPosition(position.id)"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition">
              {{ position.title }}
            </h3>
            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition">
              <button
                @click.stop="editPosition(position)"
                class="p-1 text-gray-400 hover:text-blue-600 transition"
                title="Edit Position"
              >
                <Edit class="h-4 w-4" />
              </button>
              <button
                @click.stop="deletePosition(position.id)"
                class="p-1 text-gray-400 hover:text-red-600 transition"
                title="Delete Position"
              >
                <Trash2 class="h-4 w-4" />
              </button>
              <div class="flex items-center text-gray-400">
                <Users class="h-4 w-4 mr-1" />
                <span class="text-xs">{{ position.candidates?.length || 0 }}</span>
              </div>
            </div>
          </div>
          <p class="text-sm text-gray-600 mb-3">
            {{ position.description || 'No description provided' }}
          </p>
          <div class="flex justify-between items-center text-xs text-gray-500">
            <span>Max Candidates: {{ position.max_candidates || 'N/A' }}</span>
            <span>Votes: {{ position.total_votes || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <CreatePosition 
      :show="showCreatePositionModal" 
      :electionId="electionId"
      @close="showCreatePositionModal = false"
      @save="fetchElectionAndPositions" 
    />
    
    <CreatePosition 
      :show="showEditPositionModal" 
      :electionId="electionId"
      :editingPosition="editingPosition"
      @close="showEditPositionModal = false"
      @save="fetchElectionAndPositions"
    />
  </div>
</template>
