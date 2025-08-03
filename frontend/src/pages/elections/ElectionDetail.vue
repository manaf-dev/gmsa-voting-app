<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { ref, onMounted, computed } from 'vue'
import CreatePosition from '@/modules/CreatePosition.vue'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()

const showCreatePositionModal = ref(false)
const electionId = route.params.id as string

const election = computed(() => electionStore.specificElection)
const positions = computed(() => electionStore.electionPositions)

const goBack = () => {
  router.back()
}

const fetchElectionAndPositions = async () => {
  await electionStore.fetchElectionDetails(electionId)
  await electionStore.retrievePositions(electionId)
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
        <h1 class="text-3xl font-bold text-gray-900">{{ election.title }}</h1>
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

      <p class="text-gray-600 mb-6">{{ election.description }}</p>

      <!-- Stats -->
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
          <p class="font-medium">{{ positions.length }}</p>
        </div>
        <div>
          <span class="text-gray-500">Total Votes:</span>
          <p class="font-medium">{{ election.total_votes || 0 }}</p>
        </div>
      </div>

      <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 shadow-lg rounded-xl">
        <div
          v-for="position in positions"
          :key="position.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
        >
          <h3 class="text-lg font-semibold text-gray-900">{{ position.title }}</h3>
          <p class="text-sm text-gray-600 mt-1">
            {{ position.description || 'No description provided' }}
          </p>
        </div>
      </div>
    </div>

    <CreatePosition :show="showCreatePositionModal" @close="showCreatePositionModal = false" />
  </div>
</template>
