<script setup lang="ts">
import {
  ArrowLeft,
  Check,
  ArrowBigLeft,
  ChevronsLeft,
  ChevronsRight,
  TriangleAlert,
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
          <h1 class="text-xl font-semibold text-gray-700">Vote - Election Title</h1>
        </div>
        <div class="text-sm text-gray-600"><span>Step 1 of 3</span></div>
      </div>
    </nav>
    <div class="max-w-6xl w-full mx-auto px-4 lg:px-8 py-3 md:py-5">
      <!-- Already Voted -->
      <div class="hidden text-center py-12">
        <!--I hid this div-->
        <div
          class="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
        >
          <Check class="w-8 h-8 text-green-600" />
        </div>
        <h2 class="text-2xl font-semibold text-gray-900 mb-2">You have already voted!</h2>
        <p class="text-gray-600 mb-4 text-sm">Thank you for participating in this election.</p>
        <div class="flex item-center gap-2 md:gap-4 w-max mx-auto">
          <router-link
            to="/admin"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowBigLeft class="h-5 w-5 mr-2" />
            Back to Admin
          </router-link>
          <router-link
            to="/admin"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            <!-- <ArrowBigLeft class="h-5 w-5 mr-2" /> -->
            View Elections
          </router-link>
        </div>
      </div>

      <!-- Voting Interface -->
      <div class="space-y-6">
        <!-- Progress Bar -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Voting Progress</h2>
            <span class="text-sm text-gray-600">1/3</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style="width: 33%"
            ></div>
          </div>
        </div>

        <!-- Current Position -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="mb-6">
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Position Title</h3>
            <p class="text-gray-600">Position description goes here.</p>
            <p class="text-sm text-gray-500 mt-2">Select one candidate for this position</p>
          </div>

          <!-- Candidates -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              class="p-4 border-2 rounded-lg transition-all border-gray-200 hover:border-gray-300"
            >
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <span class="text-green-600 font-semibold text-lg">A</span>
                </div>

                <!-- Candidate Details -->
                <div class="flex-1 min-w-0">
                  <h2 class="text-base font-semibold text-gray-900">Candidate's Name</h2>
                  <p class="text-sm text-gray-600">Student ID</p>
                  <p class="text-xs text-gray-500 mt-1 truncate">Level 300 | Computer Science</p>
                  <div class="relative mt-2">
                    <p class="text-sm text-gray-700 truncate pr-8">
                      Short manifesto summary goes here and will be truncated if too long for the
                      line.
                    </p>
                    <span
                      class="absolute right-0 top-0 text-sm text-blue-600 bg-white pl-1 cursor-pointer"
                    >
                      more
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex items-center justify-between gap-4 my-4 w-full">
            <BaseBtn
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ChevronsLeft class="h-5 w-5 mr-2" />
              Prev
            </BaseBtn>
            <BaseBtn
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              Next
              <ChevronsRight class="h-5 w-5 ml-2" />
            </BaseBtn>
            <BaseBtn
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              Submit Votes
            </BaseBtn>
          </div>

          <!-- Vote Summary -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Selections</h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- President -->
              <div class="flex items-center gap-8 border-b border-gray-100 pb-2">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Sample_User_Icon.png/240px-Sample_User_Icon.png"
                  alt="Candidate A"
                  class="w-10 h-10 rounded-full object-cover"
                />
                <div class="flex flex-col">
                  <span class="text-sm text-gray-600">President</span>
                  <span class="text-sm font-medium text-gray-900">Candidate A</span>
                </div>
              </div>

              <!-- Secretary -->
              <div class="flex items-center gap-8 border-b border-gray-100 pb-2">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Sample_User_Icon.png/240px-Sample_User_Icon.png"
                  alt="Candidate B"
                  class="w-10 h-10 rounded-full object-cover"
                />
                <div class="flex flex-col">
                  <span class="text-sm text-gray-600">Secretary</span>
                  <span class="text-sm font-medium text-gray-900">Candidate B</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Error State -->
      <div class="text-center py-12">
        <TriangleAlert class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-semimedium text-gray-900 mb-2">Unable to load voting interface</h3>
        <p class="text-gray-500 mb-4">
          There was an error loading the election or it may not be active.
        </p>
        <router-link
          to="/admin"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
        >
          <!-- <ArrowBigLeft class="h-5 w-5 mr-2" /> -->
          Back to Elections
        </router-link>
      </div>
    </div>
  </div>
</template>
