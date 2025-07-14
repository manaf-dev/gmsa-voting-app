<script setup lang="ts">
import { ref } from 'vue'
import CreateElectionModal from '@/modules/CreateElectionModal.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'

import { Plus } from 'lucide-vue-next'

const isModal = ref(false)
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto py-4 px-4 lg:px-8 bg-white shadow rounded">
      <div class="py-4 mb-4 border-b border-gray-200">
        <h1 class="text-2xl font-bold text-gray-900">Create New Election</h1>
        <p class="mt-1 text-sm text-gray-600">Set up a new election for GMSA members</p>
      </div>
      <!-- Form for creating a new election -->
      <form>
        <div class="grid grid-cols-1 md:grid-cols-2 md:gap-6">
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700"
              >Election Title</label
            >
            <BaseInput
              type="text"
              placeholder="e.g., GMSA Executive Elections 2025/2026"
              :required="true"
            />
          </div>

          <div>
            <label for="academic_year" class="block text-sm font-medium text-gray-700"
              >Academic Year</label
            >
            <BaseInput type="text" placeholder="2025/2026" :required="true" />
          </div>
        </div>
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700"
            >Description</label
          >
          <BaseTextArea placeholder="Brief description of the election..." />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 md:gap-6">
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700"
              >Start Date & Time</label
            >
            <BaseInput
              type="date"
              placeholder="e.g., GMSA Executive Elections 2025/2026"
              :required="true"
            />
          </div>

          <div>
            <label for="academic_year" class="block text-sm font-medium text-gray-700"
              >End Date & Time</label
            >
            <BaseInput type="date" placeholder="2025/2026" :required="true" />
          </div>
        </div>
        <div class="w-full flex items-center justify-between mb-4">
          <label class="block text-sm font-medium text-gray-700">Election Positions</label>
          <BaseBtn
            @click="isModal = true"
            class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg"
          >
            <Plus class="h-4 w-4" />
            Add Position
          </BaseBtn>
        </div>
        <CreateElectionModal v-if="isModal" @close="isModal = false" />
      </form>
    </div>
  </div>
</template>
