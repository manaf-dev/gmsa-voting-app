<script setup lang="ts">
import { ArrowBigLeft, Plus } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.back() // call the function
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <NavBar>
      <!-- Left slot -->
      <template #left>
        <BaseBtn
          class="flex items-center gap-1 text-blue-300 hover:bg-blue-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowBigLeft /> Back
        </BaseBtn>
      </template>

      <!-- Center slot -->
      <template #center>
        <h1 class="text-xl font-bold">Elections</h1>
      </template>

      <!-- Right slot -->
      <template #right>
        <span class="text-xs py-2 px-3 text-purple-800 bg-purple-100 rounded-full"> Name </span>
      </template>
    </NavBar>

    <!-- Page Content -->
    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-10 sm:mt-14">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">GMSA Elections</h2>
        <p class="mt-1 text-sm text-gray-600">
          Participate in democratic elections and make your voice heard
        </p>
      </div>

      <!-- Actions -->
      <div class="flex items-center space-x-3 my-4">
        <router-link
          to="/admin/elections/create"
          class="inline-flex w-full justify-center md:w-max items-center gap-1 cursor-pointer bg-green-600 hover:bg-green-700 hover:gap-1.5 transition-all duration-200 ease-in-out border-2 text-white px-4 py-2 rounded-lg truncate"
        >
          <Plus />
          Create Election
        </router-link>

        <router-link
          to="/admin"
          class="inline-flex w-full justify-center md:w-max items-center cursor-pointer bg-gray-50 hover:bg-gray-100 transition-all duration-200 ease-in-out border-2 px-4 py-2 rounded-lg truncate"
        >
          Admin Dashboard
        </router-link>
      </div>

      <!-- Tabs -->
      <div class="flex items-center overflow-x-auto gap-3 border-gray-200 mb-6 text-sm mt-10">
        <BaseBtn
          class="flex flex-col md:flex-row items-center whitespace-nowrap text-gray-500 pb-1 cursor-pointer hover:text-gray-700 transition-all duration-200 ease-in-out border-b-2 border-gray-500"
        >
          Active Elections
          <span class="bg-green-100 text-green-600 md:ml-2 py-0.5 px-2 rounded-full">3</span>
        </BaseBtn>

        <BaseBtn
          class="flex flex-col md:flex-row items-center whitespace-nowrap text-gray-500 pb-1 cursor-pointer hover:text-gray-700 transition-all duration-200 ease-in-out border-b-2 border-transparent"
        >
          Upcoming Elections
          <span class="bg-green-100 text-green-600 ml-2 py-0.5 px-2 rounded-full">3</span>
        </BaseBtn>

        <BaseBtn
          class="flex flex-col md:flex-row items-center whitespace-nowrap text-gray-500 pb-1 cursor-pointer hover:text-gray-700 transition-all duration-200 ease-in-out border-b-2 border-transparent"
        >
          Completed Elections
          <span class="bg-green-100 text-green-600 ml-2 py-0.5 px-2 rounded-full">3</span>
        </BaseBtn>
      </div>

      <!-- Election Card -->
      <div class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-4">
        <div class="flex items-center space-x-3 mb-2">
          <h3 class="text-lg font-semibold text-gray-900">Election Title</h3>
          <span class="py-2 px-3 rounded-full text-xs font-medium bg-green-100 text-green-700">
            Status
          </span>
        </div>
        <p class="text-gray-600 mb-4 text-sm">Brief description of the election goes here.</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Start Date:</span>
            <p class="font-medium">July 15, 2025</p>
            <p class="text-xs text-gray-400">10:00 AM</p>
          </div>
          <div>
            <span class="text-gray-500">End Date:</span>
            <p class="font-medium">July 20, 2025</p>
            <p class="text-xs text-gray-400">5:00 PM</p>
          </div>
          <div>
            <span class="text-gray-500">Total Votes:</span>
            <p class="font-medium">128</p>
          </div>
          <div>
            <span class="text-gray-500">Ends in:</span>
            <p class="font-medium">2 days</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
