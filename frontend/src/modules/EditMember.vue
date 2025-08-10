<script setup lang="ts">
import { reactive, watch, onMounted } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useToast } from 'vue-toastification'
import { useElectionStore } from '@/stores/electionStore'

const props = defineProps<{
  show: boolean
  member: any // The member to edit
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

const toast = useToast()
const electionStore = useElectionStore()

// Editable form data
const formData = reactive({
  first_name: '',
  last_name: '',
  username: '',
  student_id: '',
  phone: '',
  program: '',
  year_of_study: '',
  admission_year: '',
  status: '',
})

// Populate form when modal opens
watch(
  () => props.show,
  (newVal) => {
    if (newVal && props.member) {
      Object.assign(formData, props.member)
    }
  },
)
</script>

<template>
  <BaseModal :show="show" @close="emit('close')">
    <form class="max-h-[90vh] overflow-y-auto">
      <h1 class="text-2xl font-bold text-gray-900 text-center mb-4">Edit Member</h1>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label class="block text-sm font-medium text-gray-700">
          First Name
          <BaseInput v-model="formData.first_name" type="text" required />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Last Name
          <BaseInput v-model="formData.last_name" type="text" required />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Username
          <BaseInput v-model="formData.username" type="text" required />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Student ID
          <BaseInput v-model="formData.student_id" type="text" required />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Phone
          <BaseInput v-model="formData.phone" type="tel" />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Program
          <BaseInput v-model="formData.program" type="text" />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Year of Study
          <select
            v-model="formData.year_of_study"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 ring-green-500"
          >
            <option value="">Select year</option>
            <option value="100">100</option>
            <option value="200">200</option>
            <option value="300">300</option>
            <option value="400">400</option>
          </select>
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Admission Year
          <select
            v-model="formData.admission_year"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 ring-green-500"
          >
            <option value="">Select year</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
          </select>
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Status
          <select
            v-model="formData.status"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 ring-green-500"
          >
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
          </select>
        </label>
      </div>

      <div class="mt-6 flex justify-center">
        <BaseBtn
          type="submit"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
        >
          Save Changes
        </BaseBtn>
      </div>
    </form>
  </BaseModal>
</template>
