<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, User } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import CandidateDetailModal from '@/modules/CandidateDetailModal.vue'
import { useElectionStore } from '@/stores/electionStore'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()

const showCandidateDetailModal = ref(false)
const selectedCandidate = ref(null)
const loading = ref(false)

const positionId = route.params.positionId as string
const currentPosition = ref<any>(null)

const goBack = () => {
  router.back()
}

const viewCandidateDetails = (candidate: any) => {
  selectedCandidate.value = candidate
  showCandidateDetailModal.value = true
}

const fetchData = async () => {
  currentPosition.value = await electionStore.retrievePosition(positionId)
}

onMounted(async () => {
  try {
    loading.value = true
    await fetchData()
  } catch (error) {
    console.error('Error fetching position details:', error)
  } finally {
    loading.value = false
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

    <div v-if="!loading" class="max-w-4xl mx-auto py-4 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-6">
        <div class="text-center">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">{{ currentPosition?.title }}</h1>
        </div>
        
        <!-- Stats -->
        <div class="grid grid-cols-2 gap-4 mt-6 text-center">
          <p class="text-gray-600 mt-2 text-base sm:text-lg">
            {{ currentPosition?.description || 'No description provided' }}
          </p>
          <div>
            <span class="text-xs sm:text-sm text-gray-500">Candidates:</span>
            <p class="font-semibold text-gray-900 text-sm">
              {{ currentPosition?.candidates?.length || 0 }}
            </p>
          </div>
        </div>
      </div>

      <!-- Candidates List -->
      <div class="bg-white shadow-lg rounded-xl p-4 sm:p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Candidates</h2>

        <div
          v-if="!currentPosition?.candidates || currentPosition?.candidates.length === 0"
          class="text-center py-12 text-gray-500"
        >
          <User class="h-16 w-16 mx-auto mb-4 text-gray-300" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No candidates yet</h3>
          <p class="text-gray-500">Candidates will be added soon.</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="candidate in currentPosition?.candidates"
            :key="candidate.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer hover:border-green-300"
            @click="viewCandidateDetails(candidate)"
          >
            <!-- Candidate Header -->
            <div class="flex items-center gap-3 mb-3">
              <div class="w-12 h-12 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center">
                      <img v-if="candidate.profile_picture" :src="candidate.profile_picture" alt="" class="w-12 h-12 object-cover" />
                      <span v-else class="text-primary-600 font-medium">PO</span>
                    </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 truncate">
                  {{ candidate.user?.display_name || 'Name N/A' }}
                </h3>
                <p class="text-sm text-gray-600">{{ candidate.user?.student_id || 'ID N/A' }}</p>
              </div>
            </div>

            <!-- Candidate Details -->
            <div class="space-y-2">
              <div v-if="candidate.user?.email" class="sm:flex sm:justify-between">
                <span class="text-xs text-gray-500 font-medium">Email:</span>
                <p class="text-sm break-all">{{ candidate.user.email }}</p>
              </div>
              <div v-if="candidate.user?.year_of_study" class="sm:flex sm:justify-between">
                <span class="text-xs text-gray-500 font-medium">Year:</span>
                <p class="text-sm">{{ candidate.user.year_of_study }}</p>
              </div>
              <div v-if="candidate.user?.program" class="sm:flex sm:justify-between">
                <span class="text-xs text-gray-500 font-medium">Program:</span>
                <p class="text-sm">{{ candidate.user.program }}</p>
              </div>
              <!-- <div v-if="candidate.manifesto">
                <span class="text-xs text-gray-500 font-medium">Manifesto:</span>
                <p class="text-sm text-gray-700 mt-1 line-clamp-3">{{ candidate.manifesto }}</p>
              </div> -->
              <p class="text-xs text-green-600 mt-1 font-medium">Tap to see full details</p>
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

    <!-- Candidate Detail Modal -->
    <CandidateDetailModal
      :show="showCandidateDetailModal"
      :candidate="selectedCandidate"
      @close="showCandidateDetailModal = false"
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
