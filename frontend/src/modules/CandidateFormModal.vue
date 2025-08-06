<script setup lang="ts">
import { reactive, watch } from 'vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseModal from '@/components/BaseModal.vue'
import UserSearchDropdown from '@/components/UserSearchDropdown.vue'
import { useToast } from 'vue-toastification'
import { useElectionStore } from '@/stores/electionStore'
import { Plus, Save } from 'lucide-vue-next'

const electionStore = useElectionStore()
const toast = useToast()

const props = defineProps<{
  show: boolean
  positionId: string
  editingCandidate?: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
}>()

const candidateDetails = reactive({
  user: '',
  manifesto: '',
  order: '0',
})

// Watch for editing candidate changes
watch(
  () => props.editingCandidate,
  (newCandidate) => {
    if (newCandidate) {
      candidateDetails.user = newCandidate.user?.id || ''
      candidateDetails.manifesto = newCandidate.manifesto || ''
      candidateDetails.order = String(newCandidate.order || 0)
    } else {
      // Reset form for new candidate
      candidateDetails.user = ''
      candidateDetails.manifesto = ''
      candidateDetails.order = '0'
    }
  },
  { immediate: true },
)

const submitCandidateDetails = async () => {
  try {
    const payload = {
      ...candidateDetails,
      order: parseInt(candidateDetails.order) || 0,
      position: props.positionId,
    }

    if (props.editingCandidate) {
      await electionStore.updateCandidate(props.editingCandidate.id, payload)
      toast.success('Candidate updated successfully!')
    } else {
      await electionStore.createCandidate(props.positionId, payload)
      toast.success('Candidate created successfully!')
    }
    emit('save')
    emit('close')
  } catch (error) {
    toast.error(`Failed to ${props.editingCandidate ? 'update' : 'create'} candidate`)
  }
}
</script>

<template>
  <BaseModal :show="show" @close="emit('close')">
    <form @submit.prevent="submitCandidateDetails">
      <h1 class="text-2xl font-bold text-gray-900 mb-4 text-center">
        {{ editingCandidate ? 'Edit Candidate' : 'Add Candidate' }}
      </h1>

      <div class="space-y-4">
        <label class="block text-sm font-medium text-gray-700">
          Candidate
          <UserSearchDropdown
            v-model="candidateDetails.user"
            :selected-user-id="candidateDetails.user"
            placeholder="Search for a user by name, student ID, or email..."
            required
          />
          <p class="text-xs text-gray-500 mt-1">
            Select the user who will be the candidate for this position
          </p>
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Manifesto
          <BaseTextArea
            v-model="candidateDetails.manifesto"
            placeholder="Enter candidate's manifesto and vision..."
            rows="4"
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Order (Optional)
          <BaseInput v-model="candidateDetails.order" type="number" placeholder="0" min="0" />
          <p class="text-xs text-gray-500 mt-1">Display order for this candidate</p>
        </label>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <BaseBtn
          type="button"
          @click="emit('close')"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </BaseBtn>
        <BaseBtn
          type="submit"
          class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
        >
          <Plus v-if="!editingCandidate" class="h-4 w-4" />
          <Save v-else class="h-4 w-4" />
          {{ editingCandidate ? 'Update Candidate' : 'Add Candidate' }}
        </BaseBtn>
      </div>
    </form>
  </BaseModal>
</template>
