<script setup lang="ts">
import { ArrowLeft, Backpack, BadgeCheck, Vote, Users, UserCheck } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow border-b border-gray-200 sticky top-0 w-full">
      <div
        class="max-w-7xl w-full mx-auto px-4 lg:px-8 flex justify-between items-center py-3 md:py-5"
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
          <p class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            EC Member
          </p>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 px-4 lg:px-8">
      <!--main content-->

      <!--header-->
      <div class="md:mt-3 md:mb-8">
        <h2 class="text-2xl font-semibold text-gray-700">Electoral Commission Dashboard</h2>
        <p class="mt-1 text-sm text-gray-600">
          Manage elections, monitor participation, and oversee the voting process
        </p>
      </div>
    </div>

    <!-- Quick Stats -->
    <div
      class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 px-4 lg:px-8"
    >
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
        <div class="bg-blue-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Backpack class="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Elections</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q2-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
        <div class="bg-green-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <BadgeCheck class="w-6 h-6 text-green-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Acitve Elections</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q3-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
        <div class="bg-cyan-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Vote class="w-6 h-6 text-cyan-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Votes</p>
          <p class="text-2xl font-semibold text-gray-700">15</p>
        </div>
      </div>
      <!--Q4-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
        <div class="bg-orange-100 w-8 h-8 rounded-lg flex items-center justify-center">
          <Users class="w-6 h-6 text-orange-600" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600">Total Members</p>
          <p class="text-2xl font-semibold text-gray-700">100</p>
        </div>
      </div>
      <!--Q5-->
      <div class="bg-white rounded-lg shadow p-6 flex items-center gap-6">
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
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8 px-4 lg:px-8">
      <div class="bg-white rounded-lg shadow p-6 text-left">
        <h3 class="text-lg font-medium text-gray-700 mb-4">Election Management</h3>
        <div class="space-y-4">
          <router-link
            to="/admin/elections/create"
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white justify-center py-2 px-4 font-medium text-left"
          >
            Create New Election
          </router-link>
          <router-link
            to="/elections"
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white justify-center py-2 px-4 font-medium text-left"
          >
            Manage Active Elections
          </router-link>
          <router-link
            to="/elections"
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white justify-center py-2 px-4 font-medium text-left"
          >
            View All Elections
          </router-link>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 text-left">
        <h3 class="text-lg font-medium text-gray-700 mb-4">Member Management</h3>
        <div class="space-y-4">
          <router-link
            to="/admin/members"
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white py-2 px-4 font-medium text-left"
          >
            View All Members
          </router-link>
          <button
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white py-2 px-4 font-medium text-left"
          >
            Payment Reports
          </button>
          <button
            class="block w-full rounded-xl bg-green-700 hover:bg-green-800 text-white py-2 px-4 font-medium text-left"
          >
            Export Member Data
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
