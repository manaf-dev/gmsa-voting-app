<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/authStore'
import { Eye, EyeOff, ShieldCheck } from 'lucide-vue-next'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['changed'])

const toast = useToast()
const authStore = useAuthStore()

const PasswordDetails = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const loading = ref(false)
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

watch(
  () => props.show,
  (val) => {
    if (val) {
      PasswordDetails.old_password = ''
      PasswordDetails.new_password = ''
      PasswordDetails.confirm_password = ''
      showOld.value = false
      showNew.value = false
      showConfirm.value = false
    }
  },
)

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
    loading.value = true
    await authStore.changePassword(PasswordDetails)
    toast.success('Password changed successfully!')
    emit('changed')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Failed to change password')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto"
  >
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md relative p-6 sm:p-8 animate-fadeIn">
      <div class="flex items-center justify-center gap-2 mb-3">
        <ShieldCheck class="h-6 w-6 text-green-600" />
        <h1 class="text-2xl font-bold text-primary-600 text-center">Change Password</h1>
      </div>
      <p class="text-xs sm:text-sm text-gray-600 mb-4 text-center leading-relaxed">
        For security, please set a personal password now. Keep it confidential.
      </p>
      <form @submit.prevent="submitChangePassword" class="space-y-4">
        <!-- Old Password -->
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide"
            >Old Password</label
          >
          <div class="relative">
            <input
              v-model="PasswordDetails.old_password"
              :type="showOld ? 'text' : 'password'"
              required
              autocomplete="current-password"
              class="w-full pr-11 px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500 text-sm"
              placeholder="Current password"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
              @click="showOld = !showOld"
              :aria-label="showOld ? 'Hide password' : 'Show password'"
            >
              <EyeOff v-if="showOld" class="h-5 w-5" />
              <Eye v-else class="h-5 w-5" />
            </button>
          </div>
        </div>
        <!-- New Password -->
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide"
            >New Password</label
          >
          <div class="relative">
            <input
              v-model="PasswordDetails.new_password"
              :type="showNew ? 'text' : 'password'"
              required
              autocomplete="new-password"
              class="w-full pr-11 px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500 text-sm"
              placeholder="Min 8 characters"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
              @click="showNew = !showNew"
              :aria-label="showNew ? 'Hide password' : 'Show password'"
            >
              <EyeOff v-if="showNew" class="h-5 w-5" />
              <Eye v-else class="h-5 w-5" />
            </button>
          </div>
        </div>
        <!-- Confirm Password -->
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide"
            >Confirm New Password</label
          >
          <div class="relative">
            <input
              v-model="PasswordDetails.confirm_password"
              :type="showConfirm ? 'text' : 'password'"
              required
              autocomplete="new-password"
              class="w-full pr-11 px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500 text-sm"
              placeholder="Repeat new password"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
              @click="showConfirm = !showConfirm"
              :aria-label="showConfirm ? 'Hide password' : 'Show password'"
            >
              <EyeOff v-if="showConfirm" class="h-5 w-5" />
              <Eye v-else class="h-5 w-5" />
            </button>
          </div>
        </div>
        <div class="pt-2">
          <BaseBtn
            class="w-full btn btn-primary py-3 flex items-center justify-center cursor-pointer text-sm font-medium"
            :disabled="loading"
          >
            <span v-if="loading">Changing...</span>
            <span v-else>Change Password</span>
          </BaseBtn>
          <p class="mt-3 text-[10px] text-gray-500 leading-snug text-center">
            Use a strong password you haven't used elsewhere. You'll only see this prompt once.
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.18s ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
