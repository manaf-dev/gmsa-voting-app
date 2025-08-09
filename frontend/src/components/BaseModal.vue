<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  show: boolean
}>()

defineEmits(['close'])
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 flex items-center justify-center z-50 bg-black/50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-lg shadow-lg w-full max-w-3xl relative p-6">
      <button
        class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 cursor-pointer"
        @click="$emit('close')"
      >
        <X class="w-4 h-4 font-bold text-amber-600" />
      </button>
      <slot />
    </div>
  </div>
</template>
