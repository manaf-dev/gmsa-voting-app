<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/elections" class="text-primary-600 hover:text-primary-700">
              <ArrowLeft class="w-5 h-5" />
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Election Details</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-8">
      <!-- Election Header -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-4">
              <h1 class="text-3xl font-bold text-gray-900">GMSA Executive Elections 2025</h1>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
              >
                Active
              </span>
            </div>

            <p class="text-gray-600 mb-6">
              This election is for selecting the new executives of the GMSA for the 2025/2026
              academic year.
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Start Date:</span>
                <p class="font-medium">01 January 2025, 08:00 AM</p>
              </div>
              <div>
                <span class="text-gray-500">End Date:</span>
                <p class="font-medium">02 January 2025, 05:00 PM</p>
              </div>
              <div>
                <span class="text-gray-500">Total Positions:</span>
                <p class="font-medium">3</p>
              </div>
              <div>
                <span class="text-gray-500">Total Votes:</span>
                <p class="font-medium">120</p>
              </div>
            </div>
          </div>

          <div class="ml-6 flex flex-col space-y-2">
            <button class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              Vote Now
            </button>
          </div>
        </div>
      </div>

      <!-- Positions & Candidates -->
      <div class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-900">Positions & Candidates</h2>

        <!-- Position Card -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">President</h3>
            <p class="text-sm text-gray-600 mt-1">
              Responsible for overseeing all GMSA activities and leading the executive team.
            </p>
          </div>

          <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Candidate Card -->
            <div class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-center space-x-4 mb-4">
                <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-primary-600 font-medium">A</span>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">Ahmed Ali</h4>
                  <p class="text-sm text-gray-600">5211040227</p>
                  <p class="text-xs text-gray-500">Level 300 | Computer Science</p>
                </div>
              </div>

              <div class="mt-3">
                <h5 class="text-sm font-medium text-gray-900 mb-2">Manifesto:</h5>
                <p class="text-sm text-gray-600 line-clamp-3">
                  I aim to improve the welfare of GMSA members, enhance collaboration with other
                  organizations, and promote educational excellence.
                </p>
              </div>
            </div>

            <div class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-center space-x-4 mb-4">
                <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-primary-600 font-medium">B</span>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">Bilal Mohammed</h4>
                  <p class="text-sm text-gray-600">5211040338</p>
                  <p class="text-xs text-gray-500">Level 200 | Economics</p>
                </div>
              </div>

              <div class="mt-3">
                <h5 class="text-sm font-medium text-gray-900 mb-2">Manifesto:</h5>
                <p class="text-sm text-gray-600 line-clamp-3">
                  My goal is to foster unity and organize impactful events that promote both
                  academic and spiritual growth.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Warning -->
      <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 flex">
        <AlertTriangle class="w-5 h-5 text-amber-400 flex-shrink-0" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-amber-800">Payment Required</h3>
          <p class="text-sm text-amber-700 mt-1">
            You need to pay your annual membership dues to vote in this election.
            <router-link to="/payment/dues" class="font-medium underline hover:text-amber-600">
              Pay now
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, AlertTriangle } from 'lucide-vue-next'
</script>

{
  "id": "ef530d88-b30a-4964-8f01-5db5f655c323",
  "title": "Omnis aut modi offic",
  "description": "Rerum ducimus iusto",
  "start_date": "1983-09-09T11:20:00Z",
  "end_date": "1974-04-12T22:28:00Z",
  "status": "upcoming",
  "total_votes": 0,
  "total_voters": 0,
  "is_active": false,
  "created_by_name": "Inventore nesciunt Autem ut expedita in",
  "created_at": "2025-08-01T21:38:47.798675Z"
}
