<script setup lang="ts">
import { ArrowBigLeft, CheckCircle } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white/80 border-b border-gray-200">
      <div
        class="max-w-6xl mx-auto w-full flex items-center justify-between px-4 lg:px-8 py-3 md:py-5"
      >
        <button
          class="flex items-center gap-1 text-blue-300 hover:bg-blue-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowBigLeft />Back
        </button>
        <h1 class="text-xl font-bold">Elections Title</h1>
        <div>
          <span class="text-xs py-2 px-3 text-purple-800 bg-purple-100 rounded-full">Name</span>
        </div>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="bg-white rounded-lg shadow p-6 text-center">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">2025 University Elections</h1>
        <p class="text-gray-600 mb-4">Thank you for participating in this year's elections!</p>
        <div class="flex justify-center items-center space-x-8 text-sm">
          <div>
            <span class="text-gray-500">Election Period:</span>
            <span class="font-medium">01 July 2025 - 15 July 2025</span>
          </div>
          <div>
            <span class="text-gray-500">Total Votes Cast:</span>
            <span class="font-medium">920</span>
          </div>
          <div>
            <span class="text-gray-500">Voter Turnout:</span>
            <span class="font-medium">1200 voters</span>
          </div>
        </div>
      </div>
      <!-- Results by Position -->
      <div class="space-y-6 mt-5">
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex justify-between">
              <div>
                <h3 class="text-xl font-semibold text-gray-900">President</h3>
                <p class="text-sm text-gray-600 mt-1">Leader of the student council</p>
              </div>
              <p class="text-sm text-gray-500 text-right">Total Votes: 460</p>
            </div>
          </div>

          <div class="p-6 space-y-4">
            <div class="border rounded-lg p-4 border-green-300 bg-green-50">
              <div class="flex justify-between">
                <div class="flex items-center space-x-4">
                  <div
                    class="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium"
                  >
                    1
                  </div>
                  <div
                    class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-primary-600 font-medium">A</span>
                  </div>
                  <div>
                    <h4 class="font-semibold text-gray-900 flex items-center">
                      Alice Johnson
                      <CheckCircle class="w-5 h-5 text-green-600 ml-2" />
                    </h4>
                    <span class="text-sm text-gray-600">STD001234</span>
                    <span class="text-xs text-gray-500">Level 3 | Computer Science</span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-2xl font-bold text-gray-900">270</span>
                  <span class="text-sm text-gray-500">58.7%</span>
                </div>
              </div>
              <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="h-2 rounded-full bg-green-600" style="width: 58.7%"></div>
                </div>
              </div>
            </div>

            <div class="border rounded-lg p-4 border-gray-200">
              <div class="flex justify-between">
                <div class="flex items-center space-x-4">
                  <span
                    class="w-8 h-8 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium"
                  >
                    2
                  </span>
                  <div
                    class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-primary-600 font-medium">B</span>
                  </div>
                  <div>
                    <h4 class="font-semibold text-gray-900">Brian Smith</h4>
                    <span class="text-sm text-gray-600">STD001235</span>
                    <span class="text-xs text-gray-500">Level 2 | Engineering</span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-2xl font-bold text-gray-900">190</span>
                  <span class="text-sm text-gray-500">41.3%</span>
                </div>
              </div>
              <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="h-2 rounded-full bg-primary-600" style="width: 41.3%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-5">
        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div class="text-3xl font-bold text-blue-600 mb-2">3</div>
          <div class="text-gray-600">Positions Contested</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div class="text-3xl font-bold text-green-600 mb-2">920</div>
          <div class="text-gray-600">Total Votes Cast</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div class="text-3xl font-bold text-purple-600 mb-2">1200</div>
          <div class="text-gray-600">Voters Participated</div>
        </div>
      </div>

      <!-- Winner Announcement -->
      <div class="bg-gray-900 rounded-lg shadow text-white p-8 mt-5">
        <div class="text-center">
          <h2 class="text-2xl font-bold mb-6">🎉 Congratulations to Our Winners! 🎉</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <h3 class="font-semibold mb-2">President</h3>
              <p class="text-lg font-bold">Alice Johnson</p>
              <p class="text-sm opacity-90">270 votes (58.7%)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
