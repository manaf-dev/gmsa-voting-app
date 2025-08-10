<script setup lang="ts">
import { onMounted, ref, reactive, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { ArrowLeft, IdCard, Mail, Phone, BookOpen, CheckCircle, XCircle, User as UserIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const user = ref<any>(null)
const isSubmitting = ref(false)
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const goBack = () => router.back()

const fullName = computed(() => {
  const u = user.value
  if (!u) return ''
  return `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username || 'User'
})
const initials = computed(() => {
  const parts = fullName.value.split(' ').filter(Boolean)
  return parts.slice(0, 2).map((p: string) => p[0]?.toUpperCase() || '').join('') || 'U'
})

const activeVoteMap = computed<Record<string, boolean>>(() => user.value?.active_elections_vote_status || {})
const activeVotedCount = computed(() => Object.values(activeVoteMap.value).filter(Boolean).length)

const validatePasswordForm = () => {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    toast.error('Please fill in all password fields')
    return false
  }
  if (passwordForm.new_password.length < 8) {
    toast.error('New password must be at least 8 characters')
    return false
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    toast.error('New password and confirm password do not match')
    return false
  }
  return true
}

const changePassword = async () => {
  if (!validatePasswordForm()) return
  try {
    isSubmitting.value = true
    await authStore.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password,
    })
    toast.success('Password changed successfully!')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error: any) {
    const msg = error?.response?.data?.detail || error?.response?.data?.error || 'Failed to change password'
    toast.error(msg)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  user.value = authStore.user
})

watch(
  () => authStore.user,
  (u) => {
    user.value = u
  },
  { immediate: true }
)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <NavBar>
      <template #left>
        <button class="flex items-center text-gray-700 hover:bg-gray-100 p-2 rounded-full" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </button>
        <h1 class="text-lg font-semibold text-gray-800">Profile</h1>
      </template>
      <template #right>
        <span class="text-sm text-gray-600"> {{ fullName }} </span>
      </template>
    </NavBar>

    <!-- Header card -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-6">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xl font-semibold">
            <UserIcon class="w-8 h-8" v-if="!initials" />
            <span v-else>{{ initials }}</span>
          </div>
          <div class="flex-1">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <h2 class="text-2xl font-semibold text-gray-900">{{ fullName }}</h2>
                <p class="text-gray-600 text-sm flex items-center gap-3 mt-1">
                  <span class="inline-flex items-center gap-1"><IdCard class="w-4 h-4" /> {{ user?.student_id }}</span>
                  <span class="inline-flex items-center gap-1"><Mail class="w-4 h-4" /> {{ user?.email }}</span>
                </p>
              </div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="user?.can_vote ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'">
                  <span class="inline-flex items-center gap-1">
                    <component :is="user?.can_vote ? CheckCircle : XCircle" class="w-4 h-4" />
                    {{ user?.can_vote ? 'Eligible to vote' : 'Not eligible to vote' }}
                  </span>
                </span>
                <span v-if="user?.is_ec_member" class="px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                  EC Member
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content grid -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-10 grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left: profile details -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 class="text-base font-semibold text-gray-900">Profile Information</h3>
          </div>
          <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div class="text-xs text-gray-500">First Name</div>
              <div class="mt-1 text-gray-900">{{ user?.first_name || 'Not provided' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500">Last Name</div>
              <div class="mt-1 text-gray-900">{{ user?.last_name || 'Not provided' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500">Phone Number</div>
              <div class="mt-1 text-gray-900 inline-flex items-center gap-2"><Phone class="w-4 h-4 text-gray-500" /> {{ user?.phone_number || 'Not provided' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500">Year of Study</div>
              <div class="mt-1 text-gray-900 inline-flex items-center gap-2"><BookOpen class="w-4 h-4 text-gray-500" /> {{ user?.year_of_study ? 'Level ' + user.year_of_study : 'Not provided' }}</div>
            </div>
            <div class="md:col-span-2">
              <div class="text-xs text-gray-500">Program</div>
              <div class="mt-1 text-gray-900">{{ user?.program || 'Not provided' }}</div>
            </div>
          </div>
        </div>

        <!-- Voting status -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 class="text-base font-semibold text-gray-900">Voting Status</h3>
          </div>
          <div class="p-6">
            <div v-if="Object.keys(activeVoteMap).length === 0" class="text-sm text-gray-600">No active elections at the moment.</div>
            <div v-else class="text-sm text-gray-700 flex flex-wrap gap-2">
              <span class="text-gray-600">You have voted in</span>
              <span class="font-semibold text-gray-900">{{ activeVotedCount }}</span>
              <span class="text-gray-600">active election(s).</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: security -->
      <div class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 class="text-base font-semibold text-gray-900 mb-4">Change Password</h3>
          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-gray-600">Old Password</label>
              <div class="relative mt-1">
                <input
                  v-model="passwordForm.old_password"
                  :type="showOld ? 'text' : 'password'"
                  required
                  autocomplete="current-password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your current password"
                />
                <button type="button" class="absolute inset-y-0 right-2 text-xs text-gray-500" @click="showOld = !showOld">{{ showOld ? 'Hide' : 'Show' }}</button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600">New Password</label>
              <div class="relative mt-1">
                <input
                  v-model="passwordForm.new_password"
                  :type="showNew ? 'text' : 'password'"
                  minlength="8"
                  required
                  autocomplete="new-password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your new password"
                />
                <button type="button" class="absolute inset-y-0 right-2 text-xs text-gray-500" @click="showNew = !showNew">{{ showNew ? 'Hide' : 'Show' }}</button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600">Confirm New Password</label>
              <div class="relative mt-1">
                <input
                  v-model="passwordForm.confirm_password"
                  :type="showConfirm ? 'text' : 'password'"
                  minlength="8"
                  required
                  autocomplete="new-password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Confirm your new password"
                />
                <button type="button" class="absolute inset-y-0 right-2 text-xs text-gray-500" @click="showConfirm = !showConfirm">{{ showConfirm ? 'Hide' : 'Show' }}</button>
              </div>
            </div>
            <BaseBtn
              type="submit"
              class="w-full py-2.5 bg-green-600 text-white hover:bg-green-700 rounded-lg shadow-sm transition disabled:opacity-50 disabled:bg-gray-300 disabled:cursor-not-allowed"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'Changing...' : 'Change Password' }}
            </BaseBtn>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
