<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Mail, Phone, User, IdCard } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import EditMemberModal from '@/modules/EditMember.vue'
import { useRouter, useRoute } from 'vue-router'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useElectionStore } from '@/stores/electionStore'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route = useRoute()
const electionStore = useElectionStore()
const authStore = useAuthStore()
const toast = useToast()

const member = ref<any>(null)
const showEditModal = ref(false)
const temporaryPassword = ref<string | null>(null) // show password temporarily
const resetting = ref(false) // track reset button state
const showRemoveConfirm = ref(false)
const showResetConfirm = ref(false)

const goBack = () => {
  router.back()
}

onMounted(async () => {
  const id = route.params.id
  await electionStore.fetchUsers()
  member.value = electionStore.availableUsers.find((u) => u.id == id)
})

const handleUpdated = async () => {
  showEditModal.value = false
  await electionStore.fetchUsers()
  member.value = electionStore.availableUsers.find((u) => u.id == route.params.id)
}

const resetMemberPassword = async () => {
  if (!member.value) return
  resetting.value = true
  try {
    const res = await authStore.resetPassword(member.value.student_id)
    temporaryPassword.value = res.new_password // store temp password
    toast.success(`Password for ${member.value.first_name} has been reset.`)

    // hide after 1 min
    setTimeout(() => {
      temporaryPassword.value = null
    }, 60000)
  } catch (error) {
    toast.error('Failed to reset password.')
  } finally {
    resetting.value = false
  }
}

const confirmRemove = () => {
  showRemoveConfirm.value = true
}

const performRemove = async () => {
  if (!member.value) return
  try {
    await electionStore.removeUser(member.value.id)
    showRemoveConfirm.value = false
    router.push('/admin/members')
  } catch (e) {
    showRemoveConfirm.value = false
  }
}

const confirmReset = () => {
  showResetConfirm.value = true
}

const performReset = async () => {
  showResetConfirm.value = false
  await resetMemberPassword()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <BaseBtn
          class="flex items-center text-gray-700 hover:bg-gray-100 transition-all ease-in-out duration-200 py-1 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowLeft />
        </BaseBtn>
        <h1 class="text-xl font-semibold text-gray-700 truncate">Member Details</h1>
      </template>
    </NavBar>

    <div class="max-w-3xl mx-auto px-4 py-6 pt-20 sm:pt-24">
      <div v-if="member" class="bg-white rounded-lg shadow-md overflow-hidden">
        <!-- Show temporary password -->
        <div
          v-if="temporaryPassword"
          class="p-4 bg-green-50 border border-green-300 rounded-md m-4"
        >
          <p class="font-semibold text-green-800">New Password:</p>
          <p class="text-lg font-mono text-green-900">{{ temporaryPassword }}</p>
          <p class="text-xs text-green-700 mt-1">This will disappear in 1 minute.</p>
        </div>

        <!-- Profile header -->
        <div
          class="flex flex-col sm:flex-row items-center sm:items-start gap-4 p-6 border-b border-gray-200"
        >
          <div class="text-center sm:text-left">
            <h2 class="text-2xl font-semibold text-gray-800">
              {{ member.first_name }} {{ member.last_name }}
            </h2>
            <p class="text-gray-500">{{ member.program || 'No program specified' }}</p>
          </div>
        </div>

        <!-- Details list -->
        <div class="p-6 space-y-4">
          <div class="flex items-center gap-3 text-gray-700">
            <Mail class="h-5 w-5 text-gray-400" />
            <span>{{ member.email }}</span>
          </div>
          <div class="flex items-center gap-3 text-gray-700">
            <Phone class="h-5 w-5 text-gray-400" />
            <span>{{ member.phone || 'No phone provided' }}</span>
          </div>
          <div class="flex items-center gap-3 text-gray-700">
            <IdCard class="h-5 w-5 text-gray-400" />
            <span>Student ID: {{ member.student_id }}</span>
          </div>
          <div class="flex items-center gap-3 text-gray-700">
            <User class="h-5 w-5 text-gray-400" />
            <span>Status: {{ member.status || 'Active' }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row justify-end gap-3 p-6 border-t border-gray-200">
          <BaseBtn
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            @click="showEditModal = true"
          >
            Edit
          </BaseBtn>
          <BaseBtn class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition" @click="confirmRemove">
            Remove
          </BaseBtn>
          <BaseBtn
            class="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 transition"
            @click="confirmReset"
            :disabled="resetting"
          >
            {{ resetting ? 'Resetting...' : 'Reset Password' }}
          </BaseBtn>
        </div>
      </div>

      <div v-else class="text-center text-gray-500 py-20">Loading member details...</div>
    </div>

  <!-- Edit Modal -->
    <EditMemberModal
      :show="showEditModal"
      :member="member"
      @close="showEditModal = false"
      @updated="handleUpdated"
    />

  <!-- Confirm Modals -->
  <ConfirmModal :show="showRemoveConfirm" title="Remove Member" message="This will remove the member from the system. Proceed?" confirmText="Remove" cancelText="Cancel" @close="showRemoveConfirm = false" @confirm="performRemove" />
  <ConfirmModal :show="showResetConfirm" title="Reset Password" message="Reset this member's password and show the new temporary password?" confirmText="Reset" cancelText="Cancel" @close="showResetConfirm = false" @confirm="performReset" />
  </div>
</template>
