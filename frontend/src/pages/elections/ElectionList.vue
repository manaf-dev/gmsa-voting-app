<script setup lang="ts">
import { ArrowLeft, Plus } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useRouter } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import { useElectionStore } from '@/stores/electionStore'
import CreateElection from '@/modules/ElectionFormModal.vue'

const router = useRouter()
const electionStore = useElectionStore()
const elections = ref<any[]>([])
const loading = computed(() => electionStore.loading)
const showCreateModal = ref(false) // Track modal visibility

function goBack() {
  router.back()
}

// Format date helper
function formatDate(date: string) {
  const d = new Date(date)
  return {
    full: d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
    time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  }
}

async function fetchElections() {
  try {
    const data = await electionStore.retrieveElections()
    elections.value = data // store returns array of elections
  } catch (e) {
    // optional: handle error UI later
  }
}

onMounted(() => {
  fetchElections()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <NavBar>
      <template #left>
        <BaseBtn
          class="flex items-center gap-1 text-gray-700 hover:bg-gray-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowLeft />
        </BaseBtn>
      </template>

      <template #center>
        <h1 class="text-xl font-bold">Elections</h1>
      </template>

      <template #right>
        <span class="text-xs py-2 px-3 text-purple-800 bg-purple-100 rounded-full">Admin</span>
      </template>
    </NavBar>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">GMSA Elections</h2>
        <p class="mt-1 text-sm text-gray-600">
          Participate in democratic elections and make your voice heard
        </p>
      </div>

      <!-- Actions -->
      <div class="my-4">
        <BaseBtn
          class="inline-flex gap-3 w-full justify-center md:w-max items-center cursor-pointer bg-green-600 hover:bg-green-700 transition-all duration-200 ease-in-out px-4 py-2 rounded-lg truncate text-white"
          @click="showCreateModal = true"
        >
          <Plus class="w-4 h-4 text-white" /> New Election
        </BaseBtn>
      </div>

      <!-- Loading Skeletons -->
      <div v-if="loading" class="mt-10 relative">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
      </div>

      <!-- Election Cards -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-10">
        <div
          v-for="election in elections"
          :key="election.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-4"
          @click="router.push(`/elections/${election.id}`)"
        >
          <div class="flex items-center space-x-3 mb-2">
            <h3 class="text-lg font-semibold text-gray-900">{{ election.title }}</h3>
            <span
              class="py-1 px-3 rounded-full text-xs font-medium"
              :class="{
                'bg-green-100 text-green-700': election.status === 'active',
                'bg-blue-100 text-blue-700': election.status === 'upcoming',
                'bg-gray-100 text-gray-700': election.status === 'completed',
              }"
            >
              {{ election.status }}
            </span>
          </div>
          <p class="text-gray-600 mb-4 text-sm">{{ election.description }}</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Start Date:</span>
              <p class="font-medium">{{ formatDate(election.start_date).full }}</p>
              <p class="text-xs text-gray-400">{{ formatDate(election.start_date).time }}</p>
            </div>
            <div>
              <span class="text-gray-500">End Date:</span>
              <p class="font-medium">{{ formatDate(election.end_date).full }}</p>
              <p class="text-xs text-gray-400">{{ formatDate(election.end_date).time }}</p>
            </div>
            <div>
              <span class="text-gray-500">Created By:</span>
              <p class="font-medium">{{ election.created_by_name }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Election Modal -->
    <CreateElection :show="showCreateModal" @close="showCreateModal = false" />
  </div>
</template>
