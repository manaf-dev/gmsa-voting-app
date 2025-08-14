<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, Edit, Users, Trash2 } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { ref, onMounted, computed } from 'vue'
import PositionFormModal from '@/modules/PositionFormModal.vue'
import ElectionFormModal from '@/modules/ElectionFormModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()
const authStore = useAuthStore()

const showPositionModal = ref(false)
const editingPosition = ref(null)
const electionId = route.params.id as string
const showEditElection = ref(false)
const showDeleteElection = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref<{ type: 'position' | 'candidate'; id: string } | null>(null)

const election = ref<any>(null)
const positions = computed(() => {
  // Use positions from the election response if available, otherwise from electionPositions
  return election.value?.positions || electionStore.electionPositions || []
})

const fmt12h = (d?: string | Date) => {
  if (!d) return '-'
  const date = new Date(d)
  const datePart = date.toLocaleDateString()
  const timePart = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
  return `${datePart} ${timePart}`
}

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
  showPositionModal.value = true
}

const fetchElectionAndPositions = async () => {
  election.value = await electionStore.fetchElectionDetails(electionId)
}

const goToVote = () => {
  router.push(`/elections/${electionId}/vote`).catch((err) => {
    console.error('Navigation error:', err)
  })
}

const goToResults = () => {
  router.push(`/elections/${electionId}/results`).catch((err) => {
    console.error('Navigation error:', err)
  })
}

onMounted(() => {
  fetchElectionAndPositions()
})

const handleElectionSaved = async () => {
  await fetchElectionAndPositions()
}

const confirmDeleteElection = () => {
  showDeleteElection.value = true
}

const performDeleteElection = async () => {
  try {
    await electionStore.deleteElection(electionId)
    showDeleteElection.value = false
    router.push('/elections')
  } catch (e) {
    showDeleteElection.value = false
  }
}

const performDeleteAction = async () => {
  if (!deleteTarget.value) return
  try {
    if (deleteTarget.value.type === 'position') {
      await electionStore.deletePosition(deleteTarget.value.id)
    }
    // candidate deletion handled in PositionDetail scope; here we only cover positions listing
    await fetchElectionAndPositions()
  } finally {
    showDeleteConfirm.value = false
    deleteTarget.value = null
  }
}
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

    <div v-if="election" class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-14 sm:mt-24">
      <!-- Header -->
      <div class="flex flex-col-reverse sm:flex-row sm:items-center gap-4 justify-between">
        <h1 class="text-3xl font-bold text-gray-900">{{ election?.title }}</h1>
        <div class="flex items-center gap-4">
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-inherit hover:bg-blue-50 border-2 text-blue-700 px-4 py-2 rounded-lg cursor-pointer"
            @click="showEditElection = true"
            v-if="election.status === 'upcoming'"
          >
            Edit Election
          </BaseBtn>
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-inherit hover:bg-red-50 border-2 text-red-700 px-4 py-2 rounded-lg cursor-pointer"
            @click="confirmDeleteElection"
            v-if="election.status === 'upcoming'"
          >
            Delete Election
          </BaseBtn>
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-inherit hover:bg-green-50 border-2 text-green-700 px-4 py-2 rounded-lg cursor-pointer"
            @click="showPositionModal = true"
            v-if="election.status !== 'active' && election.status !== 'completed'"
          >
            Add Position
          </BaseBtn>
          <BaseBtn
            :class="['inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer', authStore.user?.active_elections_vote_status?.[electionId] ? 'opacity-50 pointer-events-none cursor-not-allowed' : '']"
            @click="goToVote"
            v-if="election.status === 'active'"
          >
            Cast Vote
          </BaseBtn>
          <BaseBtn
            v-if="
              election?.status === 'completed' ||
              election?.can_view_results ||
              election?.can_review_results
            "
            class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
            @click="goToResults"
          >
            View Results
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
          <p class="font-medium">{{ fmt12h(election?.start_date) }}</p>
        </div>
        <div>
          <span class="text-gray-500">End Date:</span>
          <p class="font-medium">{{ fmt12h(election?.end_date) }}</p>
        </div>
        <div>
          <span class="text-gray-500">Total Positions:</span>
          <p class="font-medium">{{ positions.length }}</p>
        </div>
      </div>

      <div
        class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 shadow-lg rounded-xl"
        v-if="positions.length"
      >
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
            <div class="flex items-center gap-2 transition">
              <button
                @click.stop="editPosition(position)"
                class="p-1 text-gray-400 hover:text-blue-600 transition cursor-pointer"
                title="Edit Position"
              >
                <Edit class="h-4 w-4" />
              </button>
              <button
                @click.stop="
                  () => (
                    (deleteTarget = { type: 'position', id: position.id }),
                    (showDeleteConfirm = true)
                  )
                "
                class="p-1 text-gray-400 hover:text-red-600 transition cursor-pointer"
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
          <!-- <div class="flex justify-between items-center text-xs text-gray-500">
            <span>Max Candidates: {{ position.max_candidates || 'N/A' }}</span>
            <span>Votes: {{ position.total_votes || 0 }}</span>
          </div> -->
        </div>
      </div>
    </div>

    <PositionFormModal
      :v-if="showPositionModal"
      :showModal="showPositionModal"
      :electionId="electionId"
      :editingPosition="editingPosition"
      @close="showPositionModal = false"
      @save="fetchElectionAndPositions"
    />

    <ElectionFormModal
      :show="showEditElection"
      :election="election"
      @close="showEditElection = false"
      @saved="handleElectionSaved"
    />
    <ConfirmModal
      :show="showDeleteElection"
      title="Delete Election"
      message="This will permanently remove the election and its positions/candidates. Proceed?"
      confirmText="Delete"
      cancelText="Cancel"
      @close="showDeleteElection = false"
      @confirm="performDeleteElection"
    />

    <ConfirmModal
      :show="showDeleteConfirm"
      title="Delete Position"
      message="This will permanently remove the position and its candidates. Proceed?"
      confirmText="Delete"
      cancelText="Cancel"
      @close="showDeleteConfirm = false"
      @confirm="performDeleteAction"
    />
  </div>
</template>
