<script setup lang="ts">
import { reactive } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/authStore'
import { useElectionStore } from '@/stores/electionStore'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'member-registered'): void
}>()

const toast = useToast()
const authStore = useAuthStore()
const electionStore = useElectionStore()

const UserDetails = reactive({
  first_name: '',
  last_name: '',
  student_id: '',
  phone: '',
  year_of_study: '',
  program: '',
  // password: '',
  // confirm_password: '',
})

const SubmitUserDetails = async () => {
  try {
    const response = await authStore.registerNewUser(UserDetails)
    toast.success('Registration successful!')
    emit('member-registered')
    emit('close') // Close modal on success
  } catch (error) {
    console.log(error)
    toast.error((error as any).response?.data?.message || 'Invalid credentials or registration failed')
  }
}
</script>

<template>
  <BaseModal :show="show" @close="emit('close')">
    <form @submit.prevent="SubmitUserDetails" class="max-h-[80vh] overflow-y-auto">
      <h1 class="text-2xl font-bold text-gray-900 text-center mb-2">Register Member</h1>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label class="block text-sm font-medium text-gray-700">
          First Name <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.first_name"
            type="text"
            placeholder="Enter your first name"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Last Name <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.last_name"
            type="text"
            placeholder="Enter your last name"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Student ID <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.student_id"
            type="number"
            placeholder="Enter your student ID"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Phone Number <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.phone"
            type="tel"
            placeholder="Enter your phone number"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Program of Study <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.program"
            type="text"
            placeholder="Enter your program"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700">
          Year of Study <span class="text-orange-500">*</span>
          <select
            v-model="UserDetails.year_of_study"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-green-500"
            required
          >
            <option disabled value="">Select year</option>
            <option value="100">100</option>
            <option value="200">200</option>
            <option value="300">300</option>
            <option value="400">400</option>
          </select>
        </label>

        <!-- <label class="block text-sm font-medium text-gray-700 mt-2">
          Password <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.password"
            type="password"
            placeholder="Enter your password"
            required
          />
        </label>

        <label class="block text-sm font-medium text-gray-700 mt-2">
          Confirm Password <span class="text-orange-500">*</span>
          <BaseInput
            v-model="UserDetails.confirm_password"
            type="password"
            placeholder="Confirm your password"
            required
          />
        </label> -->
      </div>

      <div class="w-max mx-auto mt-4">
        <BaseBtn
          type="submit"
          class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg cursor-pointer"
        >
          Add
        </BaseBtn>
      </div>
    </form>
  </BaseModal>
</template>
