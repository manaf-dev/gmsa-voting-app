<script setup lang="ts">
import BaseModal from '@/components/BaseModal.vue'
import BaseBtn from '@/components/BaseBtn.vue'

const props = defineProps<{
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirm'): void
}>()
</script>

<template>
  <BaseModal :show="props.show" @close="emit('close')">
    <div class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-900">{{ props.title || 'Confirm Action' }}</h3>
      <p class="text-sm text-gray-600">
        {{ props.message || 'Are you sure you want to proceed?' }}
      </p>
      <div class="flex justify-end gap-2 mt-4">
        <BaseBtn class="px-4 py-2 rounded-md bg-gray-100 hover:bg-gray-200" @click="emit('close')">
          {{ props.cancelText || 'Cancel' }}
        </BaseBtn>
        <BaseBtn
          class="px-4 py-2 rounded-md bg-red-600 text-white hover:bg-red-700"
          @click="emit('confirm')"
        >
          {{ props.confirmText || 'Confirm' }}
        </BaseBtn>
      </div>
    </div>
  </BaseModal>
</template>
