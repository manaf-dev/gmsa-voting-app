<script setup lang="ts">
import { reactive, watch, ref, onBeforeUnmount } from 'vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseTextArea from '@/components/BaseTextArea.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseModal from '@/components/BaseModal.vue'
import UserSearchDropdown from '@/components/UserSearchDropdown.vue'
import { useToast } from 'vue-toastification'
import { useElectionStore } from '@/stores/electionStore'
import { Plus, Save, X } from 'lucide-vue-next'

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

const fileInput = ref<HTMLInputElement | null>(null)

const candidateDetails = reactive({
  user: '',
  manifesto: '',
  order: '0',
  profile_picture: null as File | null,
  filePreview: '' as string,
})

// Watch for editing candidate changes
watch(
  () => props.editingCandidate,
  (newCandidate) => {

    if (newCandidate) {
      console.log('Editing candidate:', newCandidate)
      candidateDetails.user = newCandidate.user?.id
      candidateDetails.manifesto = newCandidate.manifesto || ''
      candidateDetails.order = String(newCandidate.order || 0)
      // candidateDetails.profile_picture = newCandidate.profile_picture
      // candidateDetails.filePreview = URL.createObjectURL(newCandidate.profile_picture) || ''
      
    } else {
      candidateDetails.user = ''
      candidateDetails.manifesto = ''
      candidateDetails.order = '0'
      candidateDetails.profile_picture = null
      candidateDetails.filePreview = ''
    }

    // clear the native file input value
    // if (fileInput.value) fileInput.value.value = ''
  },
  { immediate: true },
)

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    // revoke previous preview if present
    if (candidateDetails.filePreview) {
      try {
        URL.revokeObjectURL(candidateDetails.filePreview)
      } catch (e) {
        // ignore
      }
    }
    const f = target.files[0]
    candidateDetails.profile_picture = f
    candidateDetails.filePreview = URL.createObjectURL(f)
  }
}

const removeFile = () => {
  if (candidateDetails.filePreview) {
    try {
      URL.revokeObjectURL(candidateDetails.filePreview)
    } catch (e) {
      // ignore
    }
  }
  candidateDetails.profile_picture = null
  candidateDetails.filePreview = ''
  if (fileInput.value) fileInput.value.value = ''
}

onBeforeUnmount(() => {
  if (candidateDetails.filePreview) {
    try {
      URL.revokeObjectURL(candidateDetails.filePreview)
    } catch (e) {
      // ignore
    }
  }
})

const submitCandidateDetails = async () => {
  try {
    const formData = new FormData()
    formData.append('user', candidateDetails.user)
    formData.append('manifesto', candidateDetails.manifesto)
    formData.append('order', candidateDetails.order)
    formData.append('position', props.positionId)
    if (candidateDetails.profile_picture) {
      formData.append('profile_picture', candidateDetails.profile_picture)
    }

    if (props.editingCandidate) {
      await electionStore.updateCandidate(props.editingCandidate.id, formData)
      toast.success('Candidate updated successfully!')
    } else {
      await electionStore.createCandidate(props.positionId, formData)
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
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
            Order (Optional)
            <BaseInput v-model="candidateDetails.order" type="number" placeholder="0" min="0" />
          </label>
        </div>

        <label class="block text-sm font-medium text-gray-700">
          Manifesto
          <BaseTextArea
            v-model="candidateDetails.manifesto"
            placeholder="Enter candidate's manifesto and vision..."
            rows="4"
          />
        </label>

        <!-- File upload with fully rounded preview -->
        <label class="block text-sm font-medium text-gray-700">
          Upload Picture (Optional)
          <div v-if="candidateDetails.filePreview" class="mt-2 relative inline-block">
            <img
              :src="candidateDetails.filePreview"
              alt="Preview"
              class="h-24 w-24 object-cover rounded-full border-2 border-gray-200"
            />
            <button
              type="button"
              @click="removeFile"
              aria-label="Remove image"
              class="absolute -top-2 -right-2 bg-white text-red-600 rounded-full p-1 shadow hover:bg-gray-50"
            >
              <X class="h-4 w-4" />
            </button>
          </div>
          <div v-else class="mt-1">
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="handleFileChange"
              class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
            />
            <p class="text-xs text-gray-500 mt-1">Attach a candidate's picture (JPG, PNG, etc.)</p>
          </div>
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
