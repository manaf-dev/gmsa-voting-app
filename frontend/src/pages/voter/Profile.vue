<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-primary-600 hover:text-primary-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Profile</h1>
          </div>

          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">Display Name</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Profile Information -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Profile Information</h3>
              <button class="btn btn-outline btn-sm">Edit Profile</button>
            </div>

            <div class="p-6 space-y-6">
              <!-- Profile Picture Placeholder -->
              <div class="flex items-center space-x-6">
                <div class="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-2xl font-bold text-primary-600">U</span>
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-900">User Name</h2>
                  <p class="text-sm text-gray-600">Student ID</p>
                  <p class="text-sm text-gray-600">user@email.com</p>
                </div>
              </div>

              <!-- Profile Details -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">First Name</label>
                  <p class="mt-1 text-sm text-gray-900">Not provided</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Last Name</label>
                  <p class="mt-1 text-sm text-gray-900">Not provided</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                  <p class="mt-1 text-sm text-gray-900">Not provided</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Year of Study</label>
                  <p class="mt-1 text-sm text-gray-900">Level Not provided</p>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Program</label>
                  <p class="mt-1 text-sm text-gray-900">Not provided</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Account Status -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Account Status</h3>

            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Membership Status</span>
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                >
                  Inactive
                </span>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Dues Payment</span>
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800"
                >
                  Pending
                </span>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">EC Member</span>
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                >
                  Yes
                </span>
              </div>
            </div>

            <div class="mt-4 pt-4 border-t border-gray-200">
              <router-link to="/payment/dues" class="btn btn-primary btn-sm w-full">
                Pay Dues Now
              </router-link>
            </div>
          </div>

          <!-- Payment Summary -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Payment Summary</h3>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Total Paid</span>
                <span class="text-sm font-medium text-gray-900">₵0.00</span>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Last Payment</span>
                <span class="text-sm font-medium text-gray-900">N/A</span>
              </div>
            </div>

            <div class="mt-4 pt-4 border-t border-gray-200">
              <router-link to="/payment/donation" class="btn btn-outline btn-sm w-full">
                Make Donation
              </router-link>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>

            <div class="space-y-3">
              <router-link to="/elections" class="block w-full btn btn-outline btn-sm">
                View Elections
              </router-link>

              <router-link to="/dashboard" class="block w-full btn btn-outline btn-sm">
                Dashboard
              </router-link>

              <button class="block w-full btn btn-outline btn-sm">Admin Panel</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment History -->
      <div class="mt-8 bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Payment History</h3>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Date
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Type
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Amount
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Reference
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">01 Jan 2025</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Membership Dues</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₵0.00</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    Pending
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">REF0000</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
