<script setup lang="ts">
import router from '@/router'
import { reactive, ref } from 'vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import { useToast } from 'vue-toastification'

import { useElectionStore } from '@/stores/electionStore'
import { Plus, ArrowLeft } from 'lucide-vue-next'

const toast = useToast()
const electionStore = useElectionStore()
const isModal = ref(false)

const goBack = () => {
  router.back()
}

const ElectionDetails = reactive({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
})

const SubmitElectionDetails = async () => {
  try {
    await electionStore.createElection(ElectionDetails)
    toast.success('Election Created!')
  } catch (error) {
    toast.error('Failed to create election')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-4 lg:mx-auto py-4 px-4 lg:px-8 bg-white shadow rounded">
      <div class="py-0 md:py-4 mb-4 border-b border-gray-200">
        <button
          @click="goBack"
          class="flex items-center gap-1 text-blue-300 hover:bg-blue-50 mb-4 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowLeft class="w-5 h-5 text-gray-700" />
        </button>
        <h1 class="text-2xl font-bold text-gray-900">Create New Election</h1>
        <p class="mt-1 text-sm text-gray-600 mb-4">Set up a new election for BESA members</p>
      </div>
      <!-- Form for creating a new election -->
      <form @submit.prevent="SubmitElectionDetails">
        <div class="grid grid-cols-1">
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700"
              >Election Title</label
            >
            <BaseInput
              v-model="ElectionDetails.title"
              type="text"
              placeholder="e.g., BESA Executive Elections 2025/2026"
              :required="true"
            />
          </div>
        </div>
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700"
            >Description</label
          >
          <BaseTextArea
            v-model="ElectionDetails.description"
            placeholder="Brief description of the election..."
          />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 md:gap-6">
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700"
              >Start Date & Time</label
            >
            <BaseInput
              v-model="ElectionDetails.start_date"
              type="datetime-local"
              placeholder="e.g., BESA Executive Elections 2025/2026"
              :required="true"
            />
          </div>

          <div>
            <label for="academic_year" class="block text-sm font-medium text-gray-700"
              >End Date & Time</label
            >
            <BaseInput
              v-model="ElectionDetails.end_date"
              type="datetime-local"
              placeholder="2025/2026"
              :required="true"
            />
          </div>
        </div>
        <div class="w-full flex flex-col md:flex-row items-center justify-between mb-4 gap-2">
          <BaseBtn
            class="inline-flex w-full justify-center md:w-max items-center gap-1 cursor-pointer bg-green-600 hover:bg-green-700 hover:gap-1.5 transition-all duration-200 ease-in-out border-2 text-white px-4 py-2 rounded-lg truncate"
          >
            <Plus class="" />
            Create Election
          </BaseBtn>
          <BaseBtn
            @click="isModal = true"
            class="inline-flex w-full justify-center md:w-max items-center gap-1 cursor-pointer bg-blue-600 hover:bg-blue-700 hover:gap-1.5 transition-all duration-200 ease-in-out border-2 text-white px-4 py-2 rounded-lg truncate"
          >
            <Plus class="" />
            Add Position
          </BaseBtn>
        </div>
      </form>
    </div>
  </div>
</template>
