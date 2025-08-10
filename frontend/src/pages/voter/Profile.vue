<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, IdCard, Mail, Phone, BookOpen } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const user = ref<any>(null)
const isSubmitting = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const goBack = () => {
  router.back()
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    toast.error('New password and confirm password do not match')
    return
  }
  try {
    isSubmitting.value = true
    console.log(passwordForm) // Debug
    await authStore.changePassword(passwordForm)
    toast.success('Password changed successfully!')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    toast.error('Failed to change password')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  user.value = authStore.user
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <NavBar>
      <template #left>
        <button
          class="flex items-center text-gray-700 hover:bg-gray-100 p-2 rounded-full"
          @click="goBack"
        >
          <ArrowLeft class="w-5 h-5" />
        </button>
        <h1 class="text-lg font-semibold text-gray-800">Profile</h1>
      </template>

      <template #right>
        <span class="text-sm text-gray-600"> {{ user?.first_name }} {{ user?.last_name }} </span>
      </template>
    </NavBar>

    <div class="max-w-4xl mx-auto pt-20 pb-5 px-4 sm:px-6 lg:px-8">
      <div>
        <!-- Profile Information -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Profile Information</h3>
            </div>

            <div class="p-6 space-y-6">
              <!-- Basic Info -->
              <div class="flex items-center space-x-6">
                <div>
                  <h2 class="text-xl font-bold text-gray-900">
                    {{ user?.first_name }} {{ user?.last_name }}
                  </h2>
                  <p class="text-sm text-gray-600">
                    <IdCard class="inline w-4 h-4 mr-1" /> ID: {{ user?.student_id }}
                  </p>
                  <p class="text-sm text-gray-600">
                    <Mail class="inline w-4 h-4 mr-1" /> {{ user?.email }}
                  </p>
                </div>
              </div>

              <!-- Profile Details -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">First Name</label>
                  <p class="mt-1 text-sm text-gray-900">{{ user?.first_name || 'Not provided' }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Last Name</label>
                  <p class="mt-1 text-sm text-gray-900">{{ user?.last_name || 'Not provided' }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                  <p class="mt-1 text-sm text-gray-900">
                    <Phone class="inline w-4 h-4 mr-1" />
                    {{ user?.phone || 'Not provided' }}
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Year of Study</label>
                  <p class="mt-1 text-sm text-gray-900">
                    <BookOpen class="inline w-4 h-4 mr-1" />
                    {{ user?.year_of_study ? 'Level ' + user.year_of_study : 'Not provided' }}
                  </p>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Program</label>
                  <p class="mt-1 text-sm text-gray-900">{{ user?.program || 'Not provided' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Change Password Form -->
          <div class="bg-white rounded-xl shadow-xl p-8 mt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
            <form @submit.prevent="changePassword">
              <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
                Old Password
                <input
                  v-model="passwordForm.old_password"
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
                  v-model="passwordForm.new_password"
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
                  v-model="passwordForm.confirm_password"
                  type="password"
                  required
                  autocomplete="new-password"
                  class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                  placeholder="Confirm your new password"
                />
              </label>

              <BaseBtn
                type="submit"
                class="w-full btn btn-primary py-3 mt-5 flex items-center justify-center cursor-pointer"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? 'Changing...' : 'Change Password' }}
              </BaseBtn>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
