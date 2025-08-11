<script setup lang="ts">
import { ArrowBigLeft } from 'lucide-vue-next'
import BaseBtn from '@/components/BaseBtn.vue'
import { reactive } from 'vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const toast = useToast()
const router = useRouter()
const authStore = useAuthStore()

const PasswordDetails = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const submitChangePassword = async () => {
  if (
    !PasswordDetails.old_password ||
    !PasswordDetails.new_password ||
    !PasswordDetails.confirm_password
  ) {
    toast.error('All fields are required')
    return
  }
  if (PasswordDetails.new_password !== PasswordDetails.confirm_password) {
    toast.error('New password and confirmation do not match')
    return
  }

  try {
    await authStore.changePassword(PasswordDetails) // ✅ using store function
    toast.success('Password changed successfully!')
    router.push('/dashboard')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to change password')
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-4 text-center">

      <div class="mb-4">
        <h1 class="text-3xl font-bold text-primary-600">Change Password</h1>
        <p class="text-sm text-gray-600">Update your account password</p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-xl shadow-xl p-8">
        <form @submit.prevent="submitChangePassword">
          <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
            Old Password
            <input
              v-model="PasswordDetails.old_password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              placeholder="Enter your current password"
            />
          </label>

          <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
            New Password
            <input
              v-model="PasswordDetails.new_password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              placeholder="Enter your new password"
            />
          </label>

          <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
            Confirm New Password
            <input
              v-model="PasswordDetails.confirm_password"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              placeholder="Re-enter your new password"
            />
          </label>

          <BaseBtn
            class="w-full btn btn-primary py-3 mt-5 flex items-center justify-center cursor-pointer"
          >
            Change Password
          </BaseBtn>
        </form>
      </div>
    </div>
  </div>
</template>
