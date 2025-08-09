<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useElectionStore } from '@/stores/electionStore'
import { Search, User, ChevronDown } from 'lucide-vue-next'

const electionStore = useElectionStore()

const props = defineProps<{
  modelValue: string
  placeholder?: string
  required?: boolean
  selectedUserId?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const searchQuery = ref('')
const isOpen = ref(false)
const selectedUser = ref<any>(null) 

watch(
  () => props.selectedUserId,
  (newUserId) => {
    if (newUserId) {
      selectedUser.value = electionStore.availableUsers.find((user) => user.id === newUserId) || null
      searchQuery.value = selectedUser.value?.display_name || ''
    } else {
      selectedUser.value = null
      searchQuery.value = ''
    }
  },
  { immediate: true },
)

const filteredUsers = computed(() => {
  if (!searchQuery.value) return electionStore.availableUsers

  const query = searchQuery.value.toLowerCase()
  return electionStore.availableUsers.filter(
    (user) =>
      user.display_name?.toLowerCase().includes(query) ||
      user.student_id?.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query),
  )
})

// Computed property to check if we should show users
const shouldShowUsers = computed(() => {
  return !electionStore.loading && !electionStore.error && filteredUsers.value.length > 0
})

// Watch for modelValue changes to update selected user
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      selectedUser.value = electionStore.availableUsers.find((user) => user.id === newValue)
    } else {
      selectedUser.value = null
    }
  },
  { immediate: true },
)

// Fetch users when component mounts
watch(isOpen, async (open) => {
  if (open) {
    // Always fetch users when dropdown opens to ensure fresh data
    try {
      await electionStore.fetchUsers()
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }
})

const selectUser = (user: any) => {
  selectedUser.value = user
  emit('update:modelValue', user.id)
  isOpen.value = false
  searchQuery.value = ''
}

const openDropdown = async () => {
  isOpen.value = true
  // Fetch users immediately when opening dropdown
  try {
    await electionStore.fetchUsers()
  } catch (error) {
    console.error('Error fetching users:', error)
  }
}

const searchUsers = async () => {
  if (searchQuery.value.length > 2) {
    await electionStore.fetchUsers(searchQuery.value)
  } else if (searchQuery.value.length === 0) {
    await electionStore.fetchUsers()
  }
}

const handleFocus = async () => {
  isOpen.value = true
  // Ensure users are loaded when input is focused
  if (electionStore.availableUsers.length === 0) {
    try {
      await electionStore.fetchUsers()
    } catch (error) {
      console.error('Error fetching users on focus:', error)
    }
  }
}

// Close dropdown when clicking outside
const closeDropdown = () => {
  setTimeout(() => {
    isOpen.value = false
  }, 200)
}
</script>

<template>
  <div class="relative">
    <!-- Selected User Display / Search Input -->
    <div class="relative">
      <button
        v-if="!isOpen && selectedUser"
        @click="openDropdown"
        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <User class="h-4 w-4 text-gray-400" />
            <div class="flex flex-col">
              <span class="text-sm font-medium text-gray-900">{{ selectedUser.display_name }}</span>
              <span class="text-xs text-gray-500"
                >{{ selectedUser.student_id }} • {{ selectedUser.email }}</span
              >
            </div>
          </div>
          <ChevronDown class="h-4 w-4 text-gray-400" />
        </div>
      </button>

      <div v-else class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search class="h-4 w-4 text-gray-400" />
        </div>
        <input
          v-model="searchQuery"
          @input="searchUsers"
          @focus="handleFocus"
          @blur="closeDropdown"
          type="text"
          :placeholder="placeholder || 'Search by name, student ID, or email...'"
          :required="required"
          class="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
        />
        <button @click="openDropdown" class="absolute inset-y-0 right-0 pr-3 flex items-center">
          <ChevronDown class="h-4 w-4 text-gray-400" />
        </button>
      </div>
    </div>

    <!-- Dropdown -->
    <div
      v-if="isOpen"
      class="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
    >
      <div v-if="electionStore.loading" class="px-4 py-3 text-center text-gray-500">
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600 mx-auto"></div>
        <span class="mt-1 text-xs">Loading users...</span>
      </div>

      <div v-else-if="electionStore.error" class="px-4 py-3 text-center text-red-500">
        <p class="text-sm">{{ electionStore.error }}</p>
        <button
          @click="electionStore.fetchUsers()"
          class="text-xs text-blue-600 hover:underline mt-1"
        >
          Try again
        </button>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="px-4 py-3 text-center text-gray-500">
        <User class="h-8 w-8 mx-auto mb-2 text-gray-300" />
        <p class="text-sm">No users found</p>
        <p class="text-xs mt-1">
          {{ searchQuery ? 'Try searching with different keywords' : 'No users available' }}
        </p>
        <button
          v-if="!searchQuery"
          @click="electionStore.fetchUsers()"
          class="text-xs text-blue-600 hover:underline mt-1"
        >
          Refresh users
        </button>
      </div>

      <div v-if="shouldShowUsers">
        <button
          v-for="user in filteredUsers"
          :key="user.id"
          @click="selectUser(user)"
          class="w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none border-b border-gray-100 last:border-b-0"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <User class="h-4 w-4 text-green-600" />
            </div>
            <div class="flex flex-col min-w-0 flex-1">
              <span class="text-sm font-medium text-gray-900 truncate">{{
                user.display_name
              }}</span>
              <span class="text-xs text-gray-500 truncate"
                >{{ user.student_id }} • {{ user.email }}</span
              >
              <span v-if="user.program" class="text-xs text-gray-400 truncate"
                >{{ user.program }} - Year {{ user.year_of_study }}</span
              >
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
