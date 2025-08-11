<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, Plus, Edit, Trash2, User } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import CandidateFormModal from '@/modules/CandidateFormModal.vue'
import CandidateDetailModal from '@/modules/CandidateDetailModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useElectionStore } from '@/stores/electionStore'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()

const showCandidateFormModal = ref(false)
const showEditCandidateModal = ref(false)
const showCandidateDetailModal = ref(false)
const editingCandidate = ref(null)
const selectedCandidate = ref(null)
const Loading = ref(false)

const positionId = route.params.positionId as string
const currentPosition = ref<any>(null)

const goBack = () => {
  router.back()
}

const editCandidate = (candidate: any) => {
  editingCandidate.value = candidate
  showCandidateFormModal.value = true
}

const viewCandidateDetails = (candidate: any) => {
  selectedCandidate.value = candidate
  showCandidateDetailModal.value = true
}

const showDeleteConfirm = ref(false)
const deleteCandidateId = ref<string | null>(null)
const askDeleteCandidate = (candidateId: string) => {
  deleteCandidateId.value = candidateId
  showDeleteConfirm.value = true
}
const performDeleteCandidate = async () => {
  if (!deleteCandidateId.value) return
  try {
    await electionStore.deleteCandidate(positionId, deleteCandidateId.value)
    await fetchData()
  } catch (error) {
    console.error('Failed to delete candidate:', error)
  } finally {
    showDeleteConfirm.value = false
    deleteCandidateId.value = null
  }
}

const fetchData = async () => {
  currentPosition.value = await electionStore.retrievePosition(positionId)
}

onMounted(async () => {
  try {
    Loading.value = true
    await fetchData()
  } catch (error) {
    console.error('Error fetching positions:', error)
  } finally {
    Loading.value = false
  }
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
        <h1 class="text-xl font-semibold text-gray-700">Position Details</h1>
      </template>
    </NavBar>

    <div v-if="!Loading" class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <!-- Header -->
      <div class="flex flex-col-reverse sm:flex-row sm:items-center gap-4 justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ currentPosition?.title }}</h1>
          <p class="text-gray-600 mt-2">
            {{ currentPosition?.description || 'No description provided' }}
          </p>
        </div>
        <div class="flex items-center gap-4">
          <BaseBtn
            class="inline-flex text-sm items-center gap-2 bg-inherit hover:bg-green-50 border-2 text-green-700 px-4 py-2 rounded-lg cursor-pointer"
            @click="showCandidateFormModal = true"
          >
            <Plus class="h-4 w-4" />
            Add Candidate
          </BaseBtn>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm shadow-lg p-6 mb-6 rounded-xl">
        <div>
          <span class="text-gray-500">Election:</span>
          <p class="font-medium">{{ currentPosition?.election?.title }}</p>
        </div>
        <div>
          <span class="text-gray-500">Max Candidates:</span>
          <p class="font-medium">{{ currentPosition?.max_candidates || 'Unlimited' }}</p>
        </div>
        <div>
          <span class="text-gray-500">Current Candidates:</span>
          <p class="font-medium">{{ currentPosition?.candidates?.length || 0 }}</p>
        </div>
        <div>
          <span class="text-gray-500">Total Votes:</span>
          <p class="font-medium">{{ currentPosition?.total_votes || 0 }}</p>
        </div>
      </div>

      <!-- Candidates List -->
      <div class="bg-white shadow-lg rounded-xl p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Candidates</h2>

        <div
          v-if="!currentPosition?.candidates || currentPosition?.candidates.length === 0"
          class="text-center py-12 text-gray-500"
        >
          <User class="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No candidates yet</h3>
          <p class="text-gray-500 mb-4">Add a candidate for this position.</p>
          <BaseBtn
            class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg cursor-pointer"
            @click="showCandidateFormModal = true"
          >
            <Plus class="h-4 w-4" />
            Add First Candidate
          </BaseBtn>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="candidate in currentPosition?.candidates"
            :key="candidate.id"
            class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all cursor-pointer hover:border-green-300"
            @click="viewCandidateDetails(candidate)"
          >
            <!-- Candidate Header -->
            <div class="flex justify-between items-start mb-4">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center">
                  <img v-if="candidate.profile_picture" :src="candidate.profile_picture" alt="" class="w-12 h-12 object-cover" />
                  <span v-else class="text-primary-600 font-medium">PO</span>
              </div>
                <div>
                  <h3 class="font-semibold text-gray-900">
                    {{ candidate.user?.display_name || 'Name N/A' }}
                  </h3>
                  <p class="text-sm text-gray-600">{{ candidate.user?.student_id || 'ID N/A' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click.stop="editCandidate(candidate)"
                  class="p-1 text-gray-400 hover:text-blue-600 transition"
                  title="Edit Candidate"
                >
                  <Edit class="h-4 w-4" />
                </button>
                <button @click.stop="askDeleteCandidate(candidate.id)" class="p-1 text-gray-400 hover:text-red-600 transition" title="Delete Candidate">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </div>

            <!-- Candidate Details -->
            <div class="space-y-2">
              <div v-if="candidate.user?.email">
                <span class="text-xs text-gray-500">Email:</span>
                <p class="text-sm">{{ candidate.user.email }}</p>
              </div>
              <div v-if="candidate.user?.year_of_study">
                <span class="text-xs text-gray-500">Year:</span>
                <p class="text-sm">{{ candidate.user.year_of_study }}</p>
              </div>
              <div v-if="candidate.user?.program">
                <span class="text-xs text-gray-500">Program:</span>
                <p class="text-sm">{{ candidate.user.program }}</p>
              </div>
              <div v-if="candidate.manifesto">
                <span class="text-xs text-gray-500">Manifesto:</span>
                <p class="text-sm text-gray-700 mt-1 line-clamp-3">{{ candidate.manifesto }}</p>
                <p class="text-xs text-green-600 mt-1 font-medium">Click to read full manifesto</p>
              </div>
              <div>
                <span class="text-xs text-gray-500">Votes:</span>
                <p class="text-sm font-medium">{{ candidate.vote_count || 0 }}</p>
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
        <p class="mt-4 text-gray-500">Loading position details...</p>
      </div>
    </div>

    <!-- Modals -->
    <CandidateFormModal
      :show="showCandidateFormModal"
      :positionId="positionId"
      :editingCandidate="editingCandidate"
      @close="showCandidateFormModal = false"
      @save="fetchData()"
    />

    <CandidateDetailModal
      :show="showCandidateDetailModal"
      :candidate="selectedCandidate"
      @close="showCandidateDetailModal = false"
    />
    <ConfirmModal
      :show="showDeleteConfirm"
      title="Delete Candidate"
      message="This will remove the candidate permanently."
      confirmText="Delete"
      cancelText="Cancel"
      @close="showDeleteConfirm = false"
      @confirm="performDeleteCandidate"
    />
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
