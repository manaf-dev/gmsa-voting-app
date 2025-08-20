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
const showBulkVerifyModal = ref(false)
const showResultsModal = ref(false)
const bulkVerifyResults = ref<any>(null)
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const entries = ref<ExhibitionEntry[]>([])
// Track which entry is currently being verified (per-row state)
const verifyingEntryId = ref<string | null>(null)
const bulkVerifying = ref(false)
const Loading = ref(false)
const showVerifiedOnly = ref(false) // NEW toggle

// Pinia store
const electionStore = useElectionStore()
const toast = useToast()

// Handle user verification
const verifyEntry = async (entryId: string) => {
  if (verifyingEntryId.value) return // prevent parallel clicks
  verifyingEntryId.value = entryId
  try {
    await electionStore.verifyExhibition(entryId)
    toast.success('Member verified successfully')
    await fetchEntries()
  } catch (error) {
    toast.error('Failed to verify member')
  } finally {
    verifyingEntryId.value = null
  }
}

// Bulk verify all unverified entries
const bulkVerifyAll = async () => {
  if (bulkVerifying.value) return
  
  // Show confirmation modal instead of browser confirm
  showBulkVerifyModal.value = true
}

// Execute bulk verification after modal confirmation
const executeBulkVerification = async () => {
  bulkVerifying.value = true
  
  try {
    const response = await electionStore.bulkVerifyExhibition()
    
    // Store results for display in modal
    bulkVerifyResults.value = response
    
    // Close confirmation modal and show results modal
    showBulkVerifyModal.value = false
    showResultsModal.value = true
    
    await fetchEntries()
  } catch (error) {
    console.error('Bulk verification failed:', error)
    toast.error('Bulk verification failed. Please try again.')
    // Close confirmation modal on error
    showBulkVerifyModal.value = false
  } finally {
    bulkVerifying.value = false
  }
}

// Fetch exhibition entries
const fetchEntries = async () => {
  try {
    const response = await electionStore.fetchExhibition()
    entries.value = response.entries
  } catch (error) {
    throw error
  }
}

// Computed bindings
const filteredEntries = computed<ExhibitionEntry[]>(() => {
  let result = entries.value
  if (showVerifiedOnly.value) {
    result = result.filter((entry) => entry.is_verified)
  }
  if (searchQuery.value) {
    result = result.filter((entry) =>
      `${entry.first_name} ${entry.last_name} ${entry.phone_number}`
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()),
    )
  }
  return result
})

const unverifiedMembers = computed(() => {
  return entries.value.filter(entry => !entry.is_verified).length
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredEntries.value.length / itemsPerPage))
const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredEntries.value.slice(start, start + itemsPerPage)
})

const totalMembers = computed(() => filteredEntries.value.length)
const verifiedMembers = computed(() => entries.value.filter((entry) => entry.is_verified).length)

// Fetch entries on mount
onMounted(async () => {
  Loading.value = true
  try {
    await fetchEntries()
  } catch (error) {
    toast.error('Failed to fetch members')
  } finally {
    Loading.value = false
  }
})

// Search handler
const searchUsers = () => {
  currentPage.value = 1
}

// Navigation
const goBack = () => router.back()
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
        <div class="flex gap-2">
          <BaseBtn
            v-if="unverifiedMembers > 0"
            @click="bulkVerifyAll"
            :disabled="bulkVerifying"
            class="inline-flex items-center px-3 py-2 border border-blue-600 shadow-sm text-sm font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 transition-colors duration-200"
          >
            <CheckCheck class="h-4 w-4 mr-2" :class="{ 'animate-spin': bulkVerifying }" />
            {{ bulkVerifying ? 'Verifying All...' : 'Verify All' }}
          </BaseBtn>
          <BaseBtn
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors duration-200 truncate"
            @click="showAddMemberModal = true"
          >
            <Plus class="h-5 w-5 mr-2" />
            Member
          </BaseBtn>
        </div>
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
          <div class="mt-4 flex items-center gap-4 text-sm text-gray-600">
            <p>Total members: {{ totalMembers }}</p>
            <p>Verified members: {{ verifiedMembers }}</p>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="showVerifiedOnly" />
              Show verified only
            </label>
          </div>
        </div>

        <div v-if="Loading" class="p-6 text-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
        </div>

        <div v-else class="overflow-x-auto">
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
                      class="inline-flex items-center gap-1.5 text-white bg-green-500 px-3 py-1 rounded-md hover:bg-green-600 transition-colors disabled:opacity-60"
                      :disabled="verifyingEntryId === entry.id"
                    >
                      <template v-if="verifyingEntryId === entry.id">
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

    <!-- Bulk Verify Confirmation Modal -->
    <div v-if="showBulkVerifyModal" class="fixed inset-0 bg-gray-600/30 overflow-y-auto h-full w-full z-50">
      <div class="relative top-30 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <!-- Loading overlay for the modal -->
        <div v-if="bulkVerifying" class="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-md z-10">
          <div class="text-center">
            <RotateCw class="h-8 w-8 animate-spin text-blue-600 mx-auto mb-3" />
            <p class="text-sm text-gray-600 font-medium">Verifying entries...</p>
            <p class="text-xs text-gray-500 mt-1">This may take a few moments</p>
          </div>
        </div>
        
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
            <CheckCheck class="h-6 w-6 text-yellow-600" />
          </div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">Confirm Bulk Verification</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500 mb-4">
              This will verify all {{ unverifiedMembers }} unverified entries and automatically:
            </p>
            
            <p class="text-sm text-red-600 font-medium">This action cannot be undone.</p>
          </div>
          <div class="items-center px-4 py-3">
            <div class="flex gap-3 justify-center">
              <button
                @click="showBulkVerifyModal = false"
                :disabled="bulkVerifying"
                class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                @click="executeBulkVerification"
                :disabled="bulkVerifying"
                class="px-4 py-2 bg-blue-600 text-white text-base font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
              >
                <RotateCw v-if="bulkVerifying" class="h-4 w-4 mr-2 animate-spin" />
                <CheckCheck v-else class="h-4 w-4 mr-2" />
                {{ bulkVerifying ? 'Verifying...' : `Verify All (${unverifiedMembers})` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Verify Results Modal -->
    <div v-if="showResultsModal && bulkVerifyResults" class="fixed inset-0 bg-gray-600/30 overflow-y-auto h-full w-full z-50">
      <div class="relative top-30 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <CheckCheck class="h-6 w-6 text-green-600" />
          </div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">Bulk Verification Complete</h3>
          <div class="mt-4 px-7 py-3">
            <div class="text-sm text-left space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Entries verified:</span>
                <span class="font-semibold text-green-600">{{ bulkVerifyResults.verified_count }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">User accounts created:</span>
                <span class="font-semibold text-blue-600">{{ bulkVerifyResults.promoted_count }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">SMS notifications sent:</span>
                <span class="font-semibold text-purple-600">{{ bulkVerifyResults.sms_sent_count }}</span>
              </div>
              <div v-if="bulkVerifyResults.errors && bulkVerifyResults.errors.length > 0" class="mt-4 p-3 bg-yellow-50 rounded">
                <div class="flex justify-between">
                  <span class="text-gray-600">Errors encountered:</span>
                  <span class="font-semibold text-red-600">{{ bulkVerifyResults.errors.length }}</span>
                </div>
                <div class="mt-2 text-xs text-gray-500">
                  <details>
                    <summary class="cursor-pointer hover:text-gray-700">View error details</summary>
                    <ul class="mt-2 space-y-1">
                      <li v-for="error in bulkVerifyResults.errors" :key="error" class="text-red-600">
                        {{ error }}
                      </li>
                    </ul>
                  </details>
                </div>
              </div>
            </div>
            <p class="text-sm text-green-600 font-medium mt-4">{{ bulkVerifyResults.message }}</p>
          </div>
          <div class="items-center px-4 py-3">
            <button
              @click="showResultsModal = false"
              class="px-6 py-2 bg-green-600 text-white text-base font-medium rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-300 cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
