<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import AddMemberModal from '@/modules/AddMemberModal.vue'
import { ArrowLeft, ChevronsLeft, ChevronsRight, Plus, Download } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from 'vue-toastification'
import apiInstance from '@/services/api'

const router = useRouter()
const toast = useToast()
const showAddMemberModal = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const loading = ref(false) // NEW: loading state
const exporting = ref(false) // Export loading state

// Pinia store
const electionStore = useElectionStore()
const authStore = useAuthStore()

// Computed bindings
const filteredUsers = computed(() => {
  if (!searchQuery.value) return electionStore.availableUsers
  return electionStore.availableUsers.filter((user) =>
    `${user.first_name} ${user.last_name} ${user.student_id}`
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase()),
  )
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredUsers.value.slice(start, start + itemsPerPage)
})

const totalMembers = computed(() => filteredUsers.value.length)
 
// Fetch users on mount
const fetchUsers = async () => {
  loading.value = true
  try {
    await electionStore.fetchUsers()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})

// Search handler
const searchUsers = () => {
  currentPage.value = 1
}

// Navigation
const goBack = () => {
  router.back()
}

const goToMemberDetails = (id: string | number) => {
  router.push({ name: 'MemberDetails', params: { id } })
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

// Export exhibition register to Excel
const exportToExcel = async () => {
  try {
    exporting.value = true;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (searchQuery.value.trim()) {
      params.append('search', searchQuery.value.trim());
    }
    
    const response = await apiInstance.get('/elections/admin/members/export/excel/', {
      params: Object.fromEntries(params),
      responseType: 'blob'
    });
    
    // Create blob and download
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Generate filename with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-');
    link.download = `besa_exhibition_register_${timestamp}.xlsx`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    // Show success notification
    toast.success('Exhibition register exported successfully');
    
  } catch (error) {
    console.error('Export failed:', error);
    toast.error('Failed to export exhibition register. Please try again.');
  } finally {
    exporting.value = false;
  }
};
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
        <h1 class="text-xl font-semibold text-gray-700 truncate">Exhibition Register</h1>
      </template>
      <template #right>
        <div class="flex gap-2">
          <BaseBtn
            class="inline-flex items-center px-3 py-2 border border-green-600 shadow-sm text-sm font-medium rounded-md text-green-600 bg-white hover:bg-green-50 transition-colors duration-200"
            @click="exportToExcel"
            :disabled="exporting"
          >
            <Download class="h-4 w-4 mr-2" :class="{ 'animate-spin': exporting }" />
            {{ exporting ? 'Exporting...' : 'Export Register' }}
          </BaseBtn>
          <BaseBtn
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors duration-200 truncate"
            @click="showAddMemberModal = true"
          >
            <Plus class="h-5 w-5 mr-2" />
            Entry
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
              placeholder="Search by name or id..."
              @input="searchUsers"
            />
          </div>
          <div class="text-sm mt-4 text-gray-600 flex justify-between items-center">
            <p>Total entries: {{ totalMembers }}</p>
            <p class="text-xs text-gray-500">
              {{ searchQuery ? 'Filtered results' : 'All entries' }} • Export includes current filters
            </p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <!-- Loading spinner -->
          <div v-if="loading" class="p-6 text-center">
            <div
              class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"
            ></div>
          </div>

          <!-- Table -->
          <table v-else class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr class="uppercase text-xs font-medium text-gray-500">
                <th class="px-4 md:px-6 py-3 text-left">Member</th>
                <th class="px-6 py-3 text-left whitespace-nowrap">Student ID</th>
                <th class="px-6 py-3 text-left">Program</th>
                <th class="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="user in paginatedUsers"
                :key="user.id"
                class="hover:bg-gray-50 text-sm text-gray-900 cursor-pointer"
                @click="goToMemberDetails(user.id)"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-10 w-10 flex-shrink-0">
                      <div
                        class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center"
                      >
                        <span class="text-green-600 font-medium text-sm">
                          {{ user.first_name?.[0] }}{{ user.last_name?.[0] }}
                        </span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="font-medium">{{ user.first_name }} {{ user.last_name }}</div>
                      <div class="text-gray-500">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ user.student_id }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ user.program || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap font-medium">
                  <div class="flex space-x-3">
                    <button
                      class="text-green-600 hover:text-green-900 transition-colors duration-200"
                      @click.stop="goToMemberDetails(user.id)"
                    >
                      View
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="paginatedUsers.length === 0">
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">No entries found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between gap-2">
            <BaseBtn
              @click="firstPage"
              :disabled="currentPage === 1"
              class="px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronsLeft class="h-5 w-5" />
            </BaseBtn>
            <BaseBtn
              @click="lastPage"
              :disabled="currentPage === totalPages"
              class="px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronsRight class="h-5 w-5" />
            </BaseBtn>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Member Modal -->
    <AddMemberModal :show="showAddMemberModal" @close="showAddMemberModal = false" />
  </div>
</template>
