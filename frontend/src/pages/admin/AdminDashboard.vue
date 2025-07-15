<script setup lang="ts">
import {
  ArrowLeft,
  Backpack,
  BadgeCheck,
  Vote,
  Users,
  UserCheck,
  SquareArrowOutUpRight,
  BadgePlus,
  FileBadge2,
  BookMarked,
  ArrowUpFromLine,
} from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white/80 border-b border-gray-200 sticky top-0 w-full">
      <div
        class="max-w-6xl w-full mx-auto px-4 lg:px-8 flex justify-between items-center py-3 md:py-5"
      >
        <div class="flex items-center space-x-4">
          <router-link to="/dashboard" class="text-primary-600">
            <ArrowLeft class="w-5 h-5 text-gray-700" />
          </router-link>
          <h1 class="text-xl font-semibold text-gray-700">Dashboard</h1>
        </div>
        <div
          class="flex flex-col md:flex-row items-center justify-center md:space-x-4 space-y-0.5 md:space-y-0"
        >
          <p class="text-sm text-gray-600">Admin</p>
          <p class="px-3 py-2 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            EC Member
          </p>
        </div>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto py-6 px-4 lg:px-8">
      <!--main content-->

      <!--header-->
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
      <div
        class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg transition-shadow duration-200"
      >
        <div class="bg-blue-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Backpack class="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Elections</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q2-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-green-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <BadgeCheck class="w-6 h-6 text-green-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Acitve Elections</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q3-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-cyan-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Vote class="w-6 h-6 text-cyan-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Votes</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q4-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-orange-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Users class="w-6 h-6 text-orange-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Members</p>
          <p class="text-2xl font-semibold text-gray-700">100</p>
        </div>
      </div>
      <!--Q5-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6 hover:shadow-lg">
        <div class="bg-emerald-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <UserCheck class="w-6 h-6 text-emerald-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Paid Members</p>
          <p class="text-2xl font-semibold text-gray-700">50</p>
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
          <router-link
            to="/admin/elections/create"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <BadgePlus class="w-4 h-4 text-green-600" />
            Create New Election
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
          </router-link>
          <router-link
            to="/elections"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <FileBadge2 class="w-4 h-4 text-orange-600" />
            Manage Active Elections
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
          </router-link>
          <router-link
            to="/elections"
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <SquareArrowOutUpRight class="w-4 h-4 text-yellow-600" />
            View All Elections
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
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
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
          </router-link>
          <BaseBtn
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <BookMarked class="w-4 h-4 text-purple-600" />
            Payment Reports
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
          </BaseBtn>
          <BaseBtn
            class="flex items-center gap-1.5 w-max py-2 px-3 rounded-full hover:bg-gray-100 hover:text-gray-900 hover:gap-2 transition-all duration-200 ease-in-out"
          >
            <ArrowUpFromLine class="w-4 h-4 text-amber-600" />
            Export Member Data
            <!-- <SquareArrowOutUpRight class="w-4 h-4 text-blue-600" /> -->
          </BaseBtn>
        </div>
      </div>
    </div>
  </div>
</template>
