<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import AddMemberModal from '@/modules/AddMemberModal.vue'
import { ArrowLeft, ChevronsLeft, ChevronsRight, Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useElectionStore } from '@/stores/electionStore'

const router = useRouter()
const showAddMemberModal = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Pinia store
const electionStore = useElectionStore()

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
onMounted(() => {
  electionStore.fetchUsers()
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
        <h1 class="text-xl font-semibold text-gray-700 truncate">Members</h1>
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
          <div>
            <label class="block text-sm font-medium text-gray-700">Search</label>
            <BaseInput
              v-model="searchQuery"
              type="search"
              placeholder="Search by name or id..."
              @input="searchUsers"
            />
          </div>
          <div class="text-sm mt-4 text-gray-600 flex justify-start md:gap-4 items-center">
            <p>Total members: {{ totalMembers }}</p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
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
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">No members found.</td>
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
