<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'

import { useAuthStore } from '@/stores/authStore'
import { CheckCircle, Clock, DollarSign, FileText, LogOut, Settings, User } from 'lucide-vue-next'

const authStore = useAuthStore()

const showProfile = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggleProfile = () => {
  showProfile.value = !showProfile.value
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showProfile.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <h1 class="text-xl font-semibold text-gray-700">GMSA <span>Dashboard</span></h1>
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
          Welcome back, {{ authStore.user.first_name }}
        </h2>
        <p class="mt-1 text-sm text-gray-600 font-normal">
          {{ authStore.user.year_of_study }} | {{ authStore.user.program }}
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 my-8">
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
          <FileText class="w-6 h-6 text-amber-500 mb-2" />
          <p>
            <span class="block text-sm font-medium text-gray-600">Total Votes Cast</span>
            <span class="block text-2xl font-semibold text-gray-900">45</span>
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
          <FileText class="w-6 h-6 text-purple-500 mb-2" />
          <p>
            <span class="block text-sm font-medium text-gray-600">Completed Elections</span>
            <span class="block text-2xl font-semibold text-gray-900">2</span>
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-8">
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 text-center">Active Elections</h3>
          </div>
          <p class="p-6 text-center text-gray-500">No active elections</p>
        </div>
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 text-center">Upcoming Elections</h3>
          </div>
          <p class="p-6 text-center text-gray-500">No upcoming elections</p>
        </div>
      </div>

      <div class="mt-8 bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link to="" class="flex items-center p-4 border border-gray-200 rounded-lg">
            <FileText class="w-5 h-5 text-green-600 mr-3" />
            <span class="text-sm font-medium text-gray-900">View Elections</span>
          </router-link>
          <router-link to="" class="flex items-center p-4 border border-gray-200 rounded-lg">
            <DollarSign class="w-5 h-5 text-amber-600 mr-3" />
            <span class="text-sm font-medium text-gray-900">Make Donation</span>
          </router-link>
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
