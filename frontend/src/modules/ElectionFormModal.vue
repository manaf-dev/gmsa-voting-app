<script setup lang="ts">
import { reactive, watch, toRaw } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useToast } from 'vue-toastification'
import { Plus } from 'lucide-vue-next'
import { useElectionStore } from '@/stores/electionStore'
import { useRouter } from 'vue-router'

const toast = useToast()
const electionStore = useElectionStore()
const router = useRouter()

const props = defineProps<{
  show: boolean
  election?: any | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', payload: any): void
}>()

const ElectionDetails = reactive({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
})

watch(
  () => props.election,
  () => {
    if (props.election) {
      ElectionDetails.title = props.election.title || ''
      ElectionDetails.description = props.election.description || ''
      ElectionDetails.start_date = props.election.start_date
        ? String(props.election.start_date).slice(0, 16)
        : ''
      ElectionDetails.end_date = props.election.end_date
        ? String(props.election.end_date).slice(0, 16)
        : ''
    }
  },
  { immediate: true },
)

const SubmitElectionDetails = async () => {
  try {
    if (props.election?.id) {
      const updated = await electionStore.updateElection(props.election.id, toRaw(ElectionDetails))
      toast.success('Election updated!')
      emit('saved', updated)
      emit('close')
    } else {
      const newElection = await electionStore.createElection(toRaw(ElectionDetails))
      if (newElection?.id) {
        toast.success('Election Created!')
        emit('saved', newElection)
        emit('close')
        router.push(`/elections/${newElection.id}`)
      } else {
        toast.error('Election created but ID not found.')
      }
    }
  } catch (error) {
    toast.error('Failed to create election')
  }
}
</script>

<template>
  <BaseModal :show="show" @close="emit('close')">
    <form @submit.prevent="SubmitElectionDetails" class="">
      <h1 class="text-2xl font-bold text-gray-900 mb-4 text-center">
        {{ props.election ? 'Edit Election' : 'Create Election' }}
      </h1>

      <label class="block text-sm font-medium text-gray-700">
        Election Title
        <BaseInput
          v-model="ElectionDetails.title"
          type="text"
          placeholder="e.g., GMSA Executive Elections 2025/2026"
          required
        />
      </label>

      <label class="block text-sm font-medium text-gray-700">
        Description
        <BaseTextArea
          v-model="ElectionDetails.description"
          placeholder="Brief description of the election..."
        />
      </label>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <label class="block text-sm font-medium text-gray-700">
          Start Date & Time
          <BaseInput v-model="ElectionDetails.start_date" type="datetime-local" required />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          End Date & Time
          <BaseInput v-model="ElectionDetails.end_date" type="datetime-local" required />
        </label>
      </div>

      <div class="justify-end flex">
        <BaseBtn
          class="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 border-2 text-white px-4 py-2 rounded-lg cursor-pointer"
        >
          <Plus class="h-4 w-4" v-if="!props.election" />
          {{ props.election ? 'Save Changes' : 'Create Election' }}
        </BaseBtn>
      </div>
    </form>
  </BaseModal>
</template>
