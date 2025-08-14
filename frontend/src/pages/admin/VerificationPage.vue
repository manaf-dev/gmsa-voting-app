<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import RegisterModal from '@/modules/RegisterModal.vue'
import { ArrowLeft, ChevronsLeft, ChevronsRight, CheckCheck, RotateCw, Plus } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'

interface ExhibitionEntry {
  id: string
  student_id: string
  first_name: string
  last_name: string
  phone_number: string
  program: string
  year_of_study: string
  is_verified: boolean
  verified_at: string | null
  user_id: string | null
  source: string
  created_at: string
}

const router = useRouter()
const showAddMemberModal = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const entries = ref<ExhibitionEntry[]>([])
const verifyingUsers = ref<Set<string>>(new Set())

// Pinia store
const electionStore = useElectionStore()
const toast = useToast()

// Handle user verification
const verifyEntry = async (entryId: string) => {
  if (verifyingUsers.value.has(entryId)) return

  verifyingUsers.value.add(entryId)
  try {
    await electionStore.verifyExhibition(entryId)
    toast.success('Member verified successfully')
    // Refresh the entries list
    fetchEntries()
  } catch (error) {
    toast.error('Failed to verify member')
  } finally {
    verifyingUsers.value.delete(entryId)
  }
}

// Fetch exhibition entries
const fetchEntries = async () => {
  try {
    const response = await electionStore.fetchExhibition()
    entries.value = response.entries
  } catch (error) {
    toast.error('Failed to fetch members')
  }
}

// Computed bindings
const filteredEntries = computed<ExhibitionEntry[]>(() => {
  if (!searchQuery.value) return entries.value
  return entries.value.filter((entry) =>
    `${entry.first_name} ${entry.last_name} ${entry.phone_number}`
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase()),
  )
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredEntries.value.length / itemsPerPage))
const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredEntries.value.slice(start, start + itemsPerPage)
})

const totalMembers = computed(() => filteredEntries.value.length)

// Fetch entries on mount
onMounted(() => {
  fetchEntries()
})

// Search handler
const searchUsers = () => {
  currentPage.value = 1
}

// Navigation
const goBack = () => {
  router.back()
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}
const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}
const firstPage = () => {
  currentPage.value = 1
}
const lastPage = () => {
  currentPage.value = totalPages.value
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
        <h1 class="text-xl font-semibold text-gray-700 truncate">Register</h1>
      </template>
      <template #right>
        <BaseBtn
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors duration-200 truncate"
          @click="showAddMemberModal = true"
        >
          <Plus class="h-5 w-5 mr-2" />
          Member
        </BaseBtn>
      </template>
    </NavBar>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 pt-20 sm:pt-24">
      <div class="bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="max-w-sm">
            <label class="block text-sm font-medium text-gray-700">Search</label>
            <BaseInput
              v-model="searchQuery"
              type="search"
              placeholder="Search by name or phone number"
              @input="searchUsers"
            />
          </div>
          <div class="text-sm mt-4 text-gray-600 flex justify-start md:gap-4 items-center">
            <p>Total members: {{ totalMembers }}</p>
            <p>Verified members: {{}}</p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr class="uppercase text-xs font-medium text-gray-500">
                <th class="px-4 md:px-6 py-3 text-left">Member</th>
                <th class="px-6 py-3 text-left">Phone</th>
                <th class="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="entry in paginatedEntries"
                :key="entry.id"
                class="hover:bg-gray-50 text-sm text-gray-900"
                :class="{ 'bg-green-50': entry.is_verified }"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="ml-4">
                      <div class="font-medium">{{ entry.first_name }} {{ entry.last_name }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ entry.phone_number || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap font-medium">
                  <div class="flex space-x-3">
                    <BaseBtn
                      v-if="!entry.is_verified"
                      @click="verifyEntry(entry.id)"
                      class="inline-flex items-center gap-1.5 text-white bg-green-500 px-3 py-1 rounded-md hover:bg-green-600 transition-colors"
                      :disabled="verifyingUsers.has(entry.id)"
                    >
                      <template v-if="verifyingUsers.has(entry.id)">
                        <RotateCw class="h-3.5 w-3.5 animate-spin" />
                        Verifying...
                      </template>
                      <template v-else>
                        <CheckCheck class="h-3.5 w-3.5" />
                        Verify
                      </template>
                    </BaseBtn>
                    <span v-else class="text-green-600 flex items-center gap-1.5">
                      <CheckCheck class="h-3.5 w-3.5" />
                      Verified
                    </span>
                  </div>
                </td>
              </tr>
              <tr v-if="paginatedEntries.length === 0">
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">No members found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between">
            <BaseBtn
              @click="prevPage"
              :disabled="currentPage === 1"
              class="px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 rounded-md"
              title="Previous page"
            >
              <ChevronsLeft class="h-5 w-5" />
            </BaseBtn>
            <span class="px-4 py-2 text-sm text-gray-700">
              {{ currentPage }} of {{ totalPages }}
            </span>
            <BaseBtn
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 rounded-md"
              title="Next page"
            >
              <ChevronsRight class="h-5 w-5" />
            </BaseBtn>
          </div>
        </div>
      </div>
    </div>

    <!-- Register Member Modal -->
    <RegisterModal
      :show="showAddMemberModal"
      @close="showAddMemberModal = false"
      @member-registered="fetchEntries"
    />
  </div>
</template>
