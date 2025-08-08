<script setup lang="ts">
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import BaseBtn from '@/components/BaseBtn.vue'

import { Plus, X } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <div
    class="h-screen w-screen bg-black/50 fixed top-0 left-0 flex items-center justify-center z-50"
    @click="emit('close')"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-3xl relative m-4 md:m-6" @click.stop>
      <!-- Close Icon -->
      <button
        class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 focus:outline-none"
        @click="emit('close')"
      >
        <X class="h-5 w-5" />
      </button>

      <!-- Position Form Block -->
      <div class="space-y-0">
        <h1 class="text-2xl font-bold text-gray-900 mb-4 text-center">Create Position</h1>
        <div class="grid grid-cols-1 gap-0 md:gap-6">
          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Position Title</label>
            <BaseInput type="text" placeholder="e.g., President, Vice President" />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Description</label>
          <BaseTextArea placeholder="Brief description of the position..." class="mt-1" />
        </div>

        <!-- Button -->
        <div class="justify-end flex">
          <BaseBtn
            class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
          >
            <Plus class="h-4 w-4" />
            Create Position
          </BaseBtn>
        </div>
      </div>
    </div>
  </div>
</template>
