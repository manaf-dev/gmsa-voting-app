<script setup lang="ts">
import BaseInput from '@/components/BaseInput.vue'
import { ArrowBigLeft, ArrowUpFromLine, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-4 lg:mx-auto">
      <div class="bg-white shadow rounded-lg">
        <div
          class="flex flex-col md:flex-row md:items-center justify-between p-4 md:px-6 border-b border-gray-200"
        >
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Member Management</h1>
            <p class="mt-1 text-sm text-gray-600">Manage GMSA members and their dues status</p>
          </div>
          <div class="flex flex-col md:flex-row gap-4">
            <a
              href="/admin"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ArrowBigLeft class="h-5 w-5 mr-2" />
              Back to Admin
            </a>
            <button
              class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <ArrowUpFromLine class="h-5 w-5 mr-2" />
              Export CSV
            </button>
          </div>
        </div>

        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="grid grid-cols-1 md:grid-cols-2 md:gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Search</label>
              <BaseInput type="search" placeholder="Search by name or id..." />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Year of study</label>
              <select
                class="py-2 px-4 mt-1 mb-4 rounded-lg border-2 border-gray-300 focus:border-green-500 outline-none w-full"
              >
                <option disabled>Select Level</option>
                <option>All Levels</option>
                <option>Level 400</option>
                <option>Level 300</option>
                <option>Level 200</option>
                <option>Level 100</option>
              </select>
            </div>
          </div>
          <div class="mt-4">
            <div class="text-sm text-gray-600 flex justify-start md:gap-4 items-center">
              Total members: 0
              <span class="ml-4">Paid: 0</span>
              <span class="ml-4">Unpaid: 0</span>
            </div>
            <button class="text-sm text-green-600 hover:text-green-800">Clear Filters</button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr class="uppercase text-xs font-medium text-gray-500">
                <th class="px-4 md:px-6 py-3 text-left">Member</th>
                <th class="px-6 py-3 text-left whitespace-nowrap">Student ID</th>
                <th class="px-6 py-3 text-left">Program</th>
                <th class="px-6 py-3 text-left">Year</th>
                <th class="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr class="hover:bg-gray-50 text-sm text-gray-900">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="font-medium">John Doe</div>
                  <div class="text-gray-500">john@example.com</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">12345678</td>
                <td class="px-6 py-4 whitespace-nowrap">B.Ed Early Grade</td>
                <td class="px-6 py-4 whitespace-nowrap">3</td>
                <td class="px-6 py-4 whitespace-nowrap font-medium">
                  <div class="flex space-x-2">
                    <button class="text-green-600 hover:text-green-900">View</button>
                    <button class="text-blue-600 hover:text-blue-900">Remind</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="border-t border-gray-200 py-4 w-full">
          <div class="w-max mx-auto flex items-center space-x-2">
            <button
              class="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ChevronsLeft class="h-4 w-4 mr-2" />
            </button>
            <span>1 of 1</span>
            <Base
            <button
              class="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ChevronsRight class="h-4 w-4 mr-2" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
