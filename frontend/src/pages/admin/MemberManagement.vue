<script setup lang="ts">
import { ref } from 'vue'
import NavBar from '@/components/NavBar.vue'
import BaseBtn from '@/components/BaseBtn.vue'
import BaseInput from '@/components/BaseInput.vue'
import AddMemberModal from '@/pages/admin/AddMemberModal.vue' // your modal component
import { ArrowLeft, ChevronsLeft, ChevronsRight, Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()
const showAddMemberModal = ref(false) // modal state

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar>
      <template #left>
        <BaseBtn
          class="flex items-center text-gray-700 hover:bg-gray-100 transition-all ease-in-out duration-200 py-1 rounded-full cursor-pointer"
          @click="goBack"
        >
          <ArrowLeft />
        </BaseBtn>
        <h1 class="text-xl font-semibold text-gray-700 truncate">Members</h1>
      </template>
      <template #right>
        <BaseBtn
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors duration-200 truncate"
          @click="showAddMemberModal = true"
        >
          <Plus class="h-5 w-5 mr-2" />
          Member
        </BaseBtn>
      </template>
    </NavBar>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8 pt-20 sm:pt-24">
      <div class="bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="grid grid-cols-1">
            <div>
              <label class="block text-sm font-medium text-gray-700">Search</label>
              <BaseInput type="search" placeholder="Search by name or id..." />
            </div>
            <!-- <div>
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
            </div> -->
          </div>
          <div class="text-sm mt-4 text-gray-600 flex justify-start md:gap-4 items-center">
            <p>Total members: 0</p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr class="uppercase text-xs font-medium text-gray-500">
                <th class="px-4 md:px-6 py-3 text-left">Member</th>
                <th class="px-6 py-3 text-left whitespace-nowrap">Student ID</th>
                <th class="px-6 py-3 text-left">Program</th>
                <th class="px-6 py-3 text-left">Status</th>
                <th class="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr class="hover:bg-gray-50 text-sm text-gray-900">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-10 w-10 flex-shrink-0">
                      <div
                        class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center"
                      >
                        <span class="text-green-600 font-medium text-sm">JD</span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="font-medium">John Doe</div>
                      <div class="text-gray-500">john@example.com</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">12345678</td>
                <td class="px-6 py-4 whitespace-nowrap">B.Ed Early Grade</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                  >
                    Paid
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap font-medium">
                  <div class="flex space-x-3">
                    <button
                      class="text-green-600 hover:text-green-900 transition-colors duration-200"
                    >
                      View
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <BaseBtn
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Previous
              </BaseBtn>
              <BaseBtn
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Next
              </BaseBtn>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <BaseBtn
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
              >
                <ChevronsLeft class="h-5 w-5" />
              </BaseBtn>
              <BaseBtn
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
              >
                <ChevronsRight class="h-5 w-5" />
              </BaseBtn>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Member Modal -->
    <AddMemberModal :show="showAddMemberModal" @close="showAddMemberModal = false" />
  </div>
</template>
