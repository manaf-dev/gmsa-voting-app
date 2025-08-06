<script setup lang="ts">
import { reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseModal from '@/components/BaseModal.vue'
import { useToast } from 'vue-toastification'
import { useElectionStore } from '@/stores/electionStore'
import { Plus, Save } from 'lucide-vue-next'

const electionStore = useElectionStore()
const toast = useToast()
const route = useRoute()

const props = defineProps<{
  showModal: boolean
  electionId: string
  editingPosition: any
}>()

const emit = defineEmits<{ (e: 'close'): void; (e: 'save'): void }>()

const PositionDetails = reactive({
  title: '',
  description: '',
  max_candidates: '',
  order: '',
  election: '',
})

// Watch for editing position changes
watch(
  () => props.editingPosition,
  (newPosition) => {
    if (newPosition) {
      console.log('Editing position:', newPosition)
      PositionDetails.title = newPosition.title || ''
      PositionDetails.description = newPosition.description || ''
      PositionDetails.max_candidates = newPosition.max_candidates || ''
      PositionDetails.order = newPosition.order || ''
    }
  },
)

const SubmitPositionDetails = async () => {
  try {
    if (props.editingPosition) {
      await electionStore.updatePosition(props.editingPosition.id, PositionDetails)
      toast.success('Position updated successfully!')
    } else {
      await electionStore.createPosition(props.electionId, PositionDetails)
      toast.success('Position created successfully!')
    }
    emit('save')
    emit('close')
  } catch (error) {
    console.error('Failed to create or update position:', error)
    toast.error(`Failed to ${props.editingPosition ? 'update' : 'create'} position`)
  }
}
</script>

<template>
  <BaseModal :show="showModal" @close="emit('close')">
    <form @submit.prevent="SubmitPositionDetails">
      <h1 class="text-2xl font-bold text-gray-900 mb-4 text-center">
        {{ editingPosition ? 'Edit Position' : 'Create Position' }}
      </h1>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label class="block text-sm font-medium text-gray-700">
          Position Title
          <BaseInput
            v-model="PositionDetails.title"
            :type="'text'"
            :placeholder="'e.g., President'"
            :required="true"
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Maximum Candidates
          <BaseInput
            v-model="PositionDetails.max_candidates"
            :type="'number'"
            :placeholder="'e.g., 2'"
            :required="false"
          />
        </label>
      </div>

      <div class="grid grid-cols-1 gap-4">
        <label class="block text-sm font-medium text-gray-700">
          Order
          <BaseInput
            v-model="PositionDetails.order"
            :type="'number'"
            :placeholder="'1'"
            :required="true"
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Description
          <BaseTextArea
            v-model="PositionDetails.description"
            :placeholder="'Brief description of the position...'"
            class="mt-1"
          />
        </label>
      </div>

      <div class="justify-end flex mt-4">
        <BaseBtn
          class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
        >
          <Plus v-if="!editingPosition" class="h-4 w-4" />
          <Save v-else class="h-4 w-4" />
          {{ editingPosition ? 'Update Position' : 'Create Position' }}
        </BaseBtn>
      </div>
    </form>
  </BaseModal>
</template>
