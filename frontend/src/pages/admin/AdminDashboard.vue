<script setup lang="ts">
import {
  ArrowLeft,
  Backpack,
  Vote,
  Users,
  SquareArrowOutUpRight,
  BadgePlus,
  CheckCheck,
} from 'lucide-vue-next'

import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import CreateElection from '@/modules/ElectionFormModal.vue'
import { ref, onMounted, computed } from 'vue'
import { useElectionStore } from '@/stores/electionStore'

const electionStore = useElectionStore()
const loading = computed(() => electionStore.loading)
interface AdminStats {
  total_elections?: number
  total_members?: number
  eligible_voters?: number
}
const stats = computed<AdminStats>(() => (electionStore.adminStats as AdminStats) || {})

const showCreateElectionModal = ref(false) // Track modal visibility

onMounted(() => {
  electionStore.fetchAdminStats()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <router-link to="/dashboard" class="text-primary-600">
          <ArrowLeft class="w-5 h-5 text-gray-700" />
        </router-link>
        <h1 class="text-xl font-semibold text-gray-700">Dashboard</h1>
      </template>

      <template #right>
        <p class="text-sm text-gray-600">Admin</p>
        <p class="px-3 py-2 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          EC Member
        </p>
      </template>
    </NavBar>

    <div class="max-w-6xl mt-10 mx-auto py-6 px-4 sm:mt-14 lg:px-8">
      <!-- Header -->
      <div class="md:mb-4">
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900">
          Electoral Commission Dashboard
        </h2>
        <p class="mt-1 text-sm text-gray-600">
          Manage elections, monitor participation, and oversee the voting process
        </p>
      </div>
    </div>

    <!-- Quick Stats -->
    <div
      class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 px-4 lg:px-8"
    >
      <!-- Total Elections -->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-blue-100 w-10 h-10 rounded-lg flex items-center justify-center">
          <Backpack class="w-6 h-6 text-blue-700" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600">Total Elections</p>
          <p v-if="!loading" class="text-2xl font-semibold text-gray-700">{{ stats.total_elections || 0 }}</p>
          <div v-else class="h-7 w-16 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </div>

      <!-- Total Members -->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-orange-100 w-10 h-10 rounded-lg flex items-center justify-center">
          <Users class="w-6 h-6 text-orange-600" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600">Total Members</p>
          <p v-if="!loading" class="text-2xl font-semibold text-gray-700">{{ stats.total_members || 0 }}</p>
          <div v-else class="h-7 w-16 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </div>

      <!-- Eligible Voters -->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-emerald-100 w-10 h-10 rounded-lg flex items-center justify-center">
          <Vote class="w-6 h-6 text-emerald-600" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600">Eligible Voters</p>
          <p v-if="!loading" class="text-2xl font-semibold text-gray-700">{{ stats.eligible_voters || 0 }}</p>
          <div v-else class="h-7 w-16 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div
      class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 px-4 lg:px-8 text-sm font-medium text-gray-600"
    >
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg text-green-700 mb-2 px-3">Election Management</h3>
        <div class="space-y-2">
          <!-- Show modal when clicked -->
          <BaseBtn
            @click="showCreateElectionModal = true"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <BadgePlus class="w-4 h-4 text-green-600" />
            Create New Election
          </BaseBtn>

          <router-link
            to="/elections"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <SquareArrowOutUpRight class="w-4 h-4 text-yellow-600" />
            View All Elections
          </router-link>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg text-green-700 mb-2 px-3">Member Management</h3>
        <div class="space-y-2">
          <router-link
            to="/admin/members"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <Users class="w-4 h-4 text-blue-600" />
            View All Members
          </router-link>

          <router-link
            to="/verification"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <CheckCheck class="w-4 h-4 text-purple-600" />
            Verify Members
          </router-link>
        </div>
      </div>
    </div>

    <!-- Create Election Modal -->
    <CreateElection :show="showCreateElectionModal" @close="showCreateElectionModal = false" />
  </div>
</template>
