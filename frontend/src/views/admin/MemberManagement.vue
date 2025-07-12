<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Member Management</h1>
              <p class="mt-1 text-sm text-gray-600">Manage GMSA members and their dues status</p>
            </div>
            <div class="flex space-x-3">
              <router-link
                to="/admin"
                class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 19l-7-7 7-7"
                  ></path>
                </svg>
                Back to Admin
              </router-link>
              <button
                @click="exportMembers"
                :disabled="loading"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
                Export CSV
              </button>
            </div>
          </div>
        </div>

        <!-- Filters and Search -->
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label for="search" class="block text-sm font-medium text-gray-700">Search</label>
              <input
                type="text"
                id="search"
                v-model="filters.search"
                placeholder="Name, Student ID, Email..."
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>

            <div>
              <label for="academic-year" class="block text-sm font-medium text-gray-700"
                >Academic Year</label
              >
              <select
                id="academic-year"
                v-model="filters.academic_year"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">All Years</option>
                <option v-for="year in academicYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>

            <div>
              <label for="dues-status" class="block text-sm font-medium text-gray-700"
                >Dues Status</label
              >
              <select
                id="dues-status"
                v-model="filters.dues_status"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">All</option>
                <option value="paid">Paid</option>
                <option value="unpaid">Unpaid</option>
              </select>
            </div>

            <div>
              <label for="year-of-study" class="block text-sm font-medium text-gray-700"
                >Year of Study</label
              >
              <select
                id="year-of-study"
                v-model="filters.year_of_study"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">All Years</option>
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">5th Year</option>
                <option value="6">6th Year</option>
              </select>
            </div>
          </div>

          <div class="mt-4 flex justify-between items-center">
            <div class="text-sm text-gray-600">
              Total: {{ filteredMembers.length }} members
              <span class="ml-4">Paid: {{ paidCount }}</span>
              <span class="ml-4">Unpaid: {{ unpaidCount }}</span>
            </div>
            <button @click="clearFilters" class="text-sm text-green-600 hover:text-green-800">
              Clear Filters
            </button>
          </div>
        </div>

        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>

        <!-- Members Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Member
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Student ID
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Program
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Year
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Current Dues Status
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="member in paginatedMembers" :key="member.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ member.full_name }}</div>
                      <div class="text-sm text-gray-500">{{ member.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ member.student_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ member.program }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ member.year_of_study }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="{
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full': true,
                      'bg-green-100 text-green-800': member.current_dues_status === 'paid',
                      'bg-red-100 text-red-800': member.current_dues_status === 'unpaid',
                    }"
                  >
                    {{ member.current_dues_status === 'paid' ? 'Paid' : 'Unpaid' }}
                  </span>
                  <div
                    v-if="member.current_dues_status === 'paid' && member.last_payment_date"
                    class="text-xs text-gray-500 mt-1"
                  >
                    Paid: {{ new Date(member.last_payment_date).toLocaleDateString() }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button
                      @click="viewMemberDetails(member)"
                      class="text-green-600 hover:text-green-900"
                    >
                      View
                    </button>
                    <button
                      v-if="member.current_dues_status === 'unpaid'"
                      @click="sendPaymentReminder(member)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      Remind
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          v-if="totalPages > 1"
          class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6"
        >
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="currentPage > 1 && currentPage--"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="currentPage < totalPages && currentPage++"
              :disabled="currentPage === totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, filteredMembers.length) }} of
                {{ filteredMembers.length }} results
              </p>
            </div>
            <div>
              <nav
                class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                aria-label="Pagination"
              >
                <button
                  @click="currentPage > 1 && currentPage--"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="currentPage = page"
                  :class="{
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium': true,
                    'z-10 bg-green-50 border-green-500 text-green-600': page === currentPage,
                    'bg-white border-gray-300 text-gray-500 hover:bg-gray-50': page !== currentPage,
                  }"
                >
                  {{ page }}
                </button>
                <button
                  @click="currentPage < totalPages && currentPage++"
                  :disabled="currentPage === totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Member Details Modal -->
    <div
      v-if="selectedMember"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ selectedMember.full_name }}
          </h3>

          <div class="space-y-3">
            <div>
              <span class="text-sm font-medium text-gray-500">Email:</span>
              <span class="ml-2 text-sm text-gray-900">{{ selectedMember.email }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Student ID:</span>
              <span class="ml-2 text-sm text-gray-900">{{ selectedMember.student_id }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Program:</span>
              <span class="ml-2 text-sm text-gray-900">{{ selectedMember.program }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Year of Study:</span>
              <span class="ml-2 text-sm text-gray-900">{{ selectedMember.year_of_study }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Phone:</span>
              <span class="ml-2 text-sm text-gray-900">{{
                selectedMember.phone_number || 'Not provided'
              }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Joined:</span>
              <span class="ml-2 text-sm text-gray-900">{{
                new Date(selectedMember.date_joined).toLocaleDateString()
              }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Payment History:</span>
              <div class="mt-2 space-y-1">
                <div
                  v-for="payment in selectedMember.payment_history"
                  :key="payment.id"
                  class="text-sm"
                >
                  <span class="text-gray-900">{{ payment.academic_year }}</span>
                  <span class="ml-2 text-green-600">₵{{ payment.amount }}</span>
                  <span class="ml-2 text-gray-500">{{
                    new Date(payment.date_paid).toLocaleDateString()
                  }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              @click="selectedMember = null"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../services/api'

interface Member {
  id: number
  full_name: string
  email: string
  student_id: string
  program: string
  year_of_study: string
  phone_number?: string
  date_joined: string
  current_dues_status: 'paid' | 'unpaid'
  last_payment_date?: string
  payment_history: {
    id: number
    academic_year: string
    amount: number
    date_paid: string
  }[]
}

interface Filters {
  search: string
  academic_year: string
  dues_status: string
  year_of_study: string
}

const members = ref<Member[]>([])
const loading = ref(false)
const selectedMember = ref<Member | null>(null)
const currentPage = ref(1)
const itemsPerPage = 25

const filters = ref<Filters>({
  search: '',
  academic_year: '',
  dues_status: '',
  year_of_study: '',
})

const academicYears = ref<string[]>([])

const filteredMembers = computed(() => {
  let filtered = [...members.value]

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(
      (member) =>
        member.full_name.toLowerCase().includes(search) ||
        member.email.toLowerCase().includes(search) ||
        member.student_id.toLowerCase().includes(search),
    )
  }

  if (filters.value.academic_year) {
    // Filter by current academic year dues payment
    filtered = filtered.filter((member) =>
      member.payment_history.some(
        (payment) => payment.academic_year === filters.value.academic_year,
      ),
    )
  }

  if (filters.value.dues_status) {
    filtered = filtered.filter((member) => member.current_dues_status === filters.value.dues_status)
  }

  if (filters.value.year_of_study) {
    filtered = filtered.filter((member) => member.year_of_study === filters.value.year_of_study)
  }

  return filtered
})

const paidCount = computed(
  () => filteredMembers.value.filter((m) => m.current_dues_status === 'paid').length,
)
const unpaidCount = computed(
  () => filteredMembers.value.filter((m) => m.current_dues_status === 'unpaid').length,
)

const totalPages = computed(() => Math.ceil(filteredMembers.value.length / itemsPerPage))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => startIndex.value + itemsPerPage)

const paginatedMembers = computed(() =>
  filteredMembers.value.slice(startIndex.value, endIndex.value),
)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const fetchMembers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/members/')
    members.value = response.data.results || response.data

    // Extract unique academic years from payment history
    const years = new Set<string>()
    members.value.forEach((member) => {
      member.payment_history.forEach((payment) => {
        years.add(payment.academic_year)
      })
    })
    academicYears.value = Array.from(years).sort().reverse()
  } catch (error: any) {
    console.error('Error fetching members:', error)
    alert('Failed to load members')
  } finally {
    loading.value = false
  }
}

const exportMembers = async () => {
  try {
    const response = await api.get('/admin/members/export/', {
      responseType: 'blob',
      params: filters.value,
    })

    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `gmsa-members-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('Error exporting members:', error)
    alert('Failed to export members')
  }
}

const viewMemberDetails = (member: Member) => {
  selectedMember.value = member
}

const sendPaymentReminder = async (member: Member) => {
  try {
    await api.post(`/admin/members/${member.id}/send-reminder/`)
    alert(`Payment reminder sent to ${member.full_name}`)
  } catch (error: any) {
    console.error('Error sending reminder:', error)
    alert('Failed to send payment reminder')
  }
}

const clearFilters = () => {
  filters.value = {
    search: '',
    academic_year: '',
    dues_status: '',
    year_of_study: '',
  }
  currentPage.value = 1
}

// Reset to page 1 when filters change
watch(
  filters,
  () => {
    currentPage.value = 1
  },
  { deep: true },
)

onMounted(() => {
  fetchMembers()
})
</script>
