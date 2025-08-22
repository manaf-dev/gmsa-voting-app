<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'

import { useAuthStore } from '@/stores/authStore'
import { useElectionStore } from '@/stores/electionStore'
import { DollarSign, LogOut, Settings, User, Calendar } from 'lucide-vue-next'

const authStore = useAuthStore()
const electionStore = useElectionStore()

const showProfile = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const loading = ref(false)

const toggleProfile = () => {
  showProfile.value = !showProfile.value
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showProfile.value = false
  }
}

// Filter elections by status
const activeElections = computed(() => {
  return electionStore.availableElections.filter((election: any) => election.status === 'active')
})

const upcomingElections = computed(() => {
  return electionStore.availableElections.filter((election: any) => election.status === 'upcoming')
})

const completedElections = computed(() => {
  return electionStore.availableElections.filter((election: any) => election.status === 'completed')
})

const fetchElections = async () => {
  try {
    loading.value = true
    await electionStore.retrieveElections()
  } catch (error) {
    console.error('Error fetching elections:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchElections()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})


</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <h1 class="text-xl font-semibold text-gray-700">BESA <span>Dashboard</span></h1>
      </template>

      <template #right>
        <div class="flex items-center space-x-4 text-sm text-gray-600 relative" ref="dropdownRef">
          <div class="relative flex-shrink-0">
            <BaseBtn
              @click.stop="toggleProfile"
              class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center"
            >
              <span class="text-primary-600 font-medium">
                {{ authStore.user.first_name.charAt(0) }}{{ authStore.user.last_name.charAt(0) }}
              </span>
            </BaseBtn>

            <transition name="fade">
              <div
                v-if="showProfile"
                class="absolute top-10 right-0 bg-white border border-gray-200 rounded-lg shadow-lg w-40 z-50"
              >
                <router-link
                  to="/profile"
                  class="flex items-center p-3 hover:bg-gray-50 transition rounded-t-lg"
                >
                  <User class="w-5 h-5 text-green-600 mr-3" />
                  <span class="text-sm font-normal text-gray-900 truncate">My Profile</span>
                </router-link>
                <button
                  @click="authStore.logout"
                  class="flex items-center w-full p-3 hover:bg-gray-50 transition rounded-b-lg"
                >
                  <LogOut class="w-5 h-5 text-red-400 mr-3" />
                  <span class="text-sm font-normal text-gray-900">Logout</span>
                </button>
              </div>
            </transition>
          </div>
        </div>
      </template>
    </NavBar>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-14">
      <div>
        <h2 class="text-xl sm:text-2xl font-semibold text-gray-700">
          Welcome {{ authStore.user.first_name }},
        </h2>
        <p class="mt-1 text-sm text-gray-600 font-normal">
          {{ authStore.user.year_of_study }} | {{ authStore.user.program }}
        </p>
      </div>

      <!-- <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 my-8">
        <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
          <CheckCircle class="w-6 h-6 text-green-500 mb-2" />
          <p>
            <span class="block text-sm font-medium text-gray-600">Active Elections</span>
            <span class="block text-2xl font-semibold text-gray-900">2</span>
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
          <Clock class="w-6 h-6 text-blue-500 mb-2" />
          <p>
            <span class="block text-sm font-medium text-gray-600">Upcoming Elections</span>
            <span class="block text-2xl font-semibold text-gray-900">1</span>
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
          <FileText class="w-6 h-6 text-purple-500 mb-2" />
          <p>
            <span class="block text-sm font-medium text-gray-600">Completed Elections</span>
            <span class="block text-2xl font-semibold text-gray-900">2</span>
          </p>
        </div>
      </div> -->

      <div class="mt-8 space-y-6">
        <!-- Active Elections -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 text-center">Active Elections</h3>
          </div>
          <div v-if="loading" class="p-6 text-center">
            <div
              class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"
            ></div>
            <p class="mt-2 text-sm text-gray-500">Loading elections...</p>
          </div>
          <div v-else-if="activeElections.length === 0" class="p-6 text-center text-gray-500">
            No active elections
          </div>
          <div v-else class="p-4 space-y-3">
            <div
              v-for="election in activeElections"
              :key="election.id"
              class="border border-gray-200 rounded-lg p-4 hover:border-green-300 hover:shadow-md transition-all"
            >
              <div class="space-y-3">
                <div>
                  <h4 class="font-semibold text-gray-900 text-lg">{{ election.title }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ election.description }}</p>
                  <p v-if="election.is_candidate" class="text-xs mt-1 px-2 py-1 inline-block rounded-full bg-amber-100 text-amber-800">You're a candidate</p>
                </div>

                <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span class="flex items-center gap-1">
                    <Calendar class="h-3 w-3" />
                    Started {{ new Date(election.start_date).toLocaleDateString() }}
                  </span>
                  <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium"
                    >Active</span
                  >
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row gap-2 pt-2">
                  <router-link
                    :to="`/elections/${election.id}/vote`"
                    :class="[
                      'flex-1 bg-green-600 hover:bg-green-700 text-white text-center py-3 px-4 rounded-lg font-medium transition-colors',
                      authStore.user?.active_elections_vote_status?.[election.id] ? 'opacity-50 pointer-events-none cursor-not-allowed' : ''
                    ]"
                  >
                    🗳️ Cast Your Vote
                  </router-link>
                  <!-- <router-link
                    v-else
                    :to="`/elections/${election.id}/results`"
                    class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-center py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    📊 View Results
                  </router-link> -->
                  <router-link
                    :to="`/voter/elections/${election.id}`"
                    class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-center py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    View Details
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Elections -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 text-center">Upcoming Elections</h3>
          </div>
          <div v-if="loading" class="p-6 text-center">
            <div
              class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"
            ></div>
            <p class="mt-2 text-sm text-gray-500">Loading elections...</p>
          </div>
          <div v-else-if="upcomingElections.length === 0" class="p-6 text-center text-gray-500">
            No upcoming elections
          </div>
          <div v-else class="p-4 space-y-3">
            <div
              v-for="election in upcomingElections"
              :key="election.id"
              class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
            >
              <div class="space-y-3">
                <div>
                  <h4 class="font-semibold text-gray-900 text-lg">{{ election.title }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ election.description }}</p>
                </div>

                <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span class="flex items-center gap-1">
                    <Calendar class="h-3 w-3" />
                    Starts {{ new Date(election.start_date).toLocaleDateString() }}
                  </span>
                  <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium"
                    >Upcoming</span
                  >
                </div>

                <!-- Action Button -->
                <div class="pt-2">
                  <router-link
                    :to="`/voter/elections/${election.id}`"
                    class="block w-full bg-blue-100 hover:bg-blue-200 text-blue-700 text-center py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    View Details
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed Elections -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 text-center">Completed Elections</h3>
          </div>
          <div v-if="loading" class="p-6 text-center">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-500">Loading elections...</p>
          </div>
          <div v-else-if="completedElections.length === 0" class="p-6 text-center text-gray-500">
            No completed elections
          </div>
          <div v-else class="p-4 space-y-3">
            <div v-for="election in completedElections" :key="election.id" class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-md transition-all">
              <div class="space-y-3">
                <div>
                  <h4 class="font-semibold text-gray-900 text-lg">{{ election.title }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ election.description }}</p>
                </div>
                <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span class="bg-gray-100 text-gray-800 px-2 py-1 rounded-full font-medium">Completed</span>
                </div>
                <div class="flex flex-col sm:flex-row gap-2 pt-2">
                  <router-link
                    :to="`/elections/${election.id}/results`"
                    :class="['flex-1', 'bg-indigo-600', 'hover:bg-indigo-700', 'text-white', 'text-center', 'py-3', 'px-4', 'rounded-lg', 'font-medium', 'transition-colors', !election.results_published ? 'opacity-50 pointer-events-none cursor-not-allowed' : '']"
                  >
                    📊 View Results
                  </router-link>
                  <router-link
                    :to="`/voter/elections/${election.id}`"
                    class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-center py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    View Details
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- <router-link to="" class="flex items-center p-4 border border-gray-200 rounded-lg">
            <DollarSign class="w-5 h-5 text-amber-600 mr-3" />
            <span class="text-sm font-medium text-gray-900">Donate to BESA</span>
          </router-link> -->
          <router-link
            to="/admin"
            v-if="authStore.user.is_ec_member === true"
            class="flex items-center p-4 border border-gray-200 rounded-lg"
          >
            <Settings class="w-5 h-5 text-purple-600 mr-3" />
            <span class="text-sm font-medium text-gray-900">Admin Panel</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <!-- <ChangePasswordModal
      v-if="showChangePasswordModal"
      :show="showChangePasswordModal"
      @close="() => {}"
      @password-changed="refreshUser"
    /> -->
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
