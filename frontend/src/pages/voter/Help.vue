<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-green-600 hover:text-green-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <h1 class="text-xl font-bold text-gray-900">Help & Support</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-3xl font-bold text-gray-900">Help & Support</h1>
        <p class="mt-4 text-lg text-gray-600">
          Find answers to common questions or get in touch with us
        </p>
      </div>

      <!-- Quick Help -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div
            class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-6 h-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
              />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Payment Issues</h3>
          <p class="text-sm text-gray-600 mb-4">Having trouble with dues payment or donations?</p>
          <router-link
            to="/payment/dues"
            class="text-green-600 hover:text-green-800 text-sm font-medium"
          >
            Go to Payment →
          </router-link>
        </div>

        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div
            class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-6 h-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Voting Help</h3>
          <p class="text-sm text-gray-600 mb-4">Need help with the voting process?</p>
          <router-link
            to="/elections"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View Elections →
          </router-link>
        </div>

        <div class="bg-white rounded-lg shadow p-6 text-center">
          <div
            class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-6 h-6 text-purple-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Account Issues</h3>
          <p class="text-sm text-gray-600 mb-4">Problems with your account or profile?</p>
          <router-link
            to="/profile"
            class="text-purple-600 hover:text-purple-800 text-sm font-medium"
          >
            Manage Profile →
          </router-link>
        </div>
      </div>

      <!-- FAQ Section -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">Frequently Asked Questions</h2>
        </div>
        <div class="p-6">
          <dl class="space-y-6">
            <div>
              <dt class="text-lg font-medium text-gray-900">How do I pay my membership dues?</dt>
              <dd class="mt-2 text-gray-600">
                You can pay your membership dues through the Payment section using Paystack.
                Navigate to "Payment" in your dashboard, select "Membership Dues," enter the amount
                (₵{{ duesAmount }}), and complete the payment process. You'll receive a confirmation
                once payment is successful.
              </dd>
            </div>

            <div>
              <dt class="text-lg font-medium text-gray-900">Why can't I vote in elections?</dt>
              <dd class="mt-2 text-gray-600">
                To vote in GMSA elections, you must have paid your membership dues for the current
                academic year. If you haven't paid, you'll see a payment reminder when accessing
                elections. Complete your dues payment and you'll be able to vote immediately.
              </dd>
            </div>

            <div>
              <dt class="text-lg font-medium text-gray-900">How does the voting process work?</dt>
              <dd class="mt-2 text-gray-600">
                Once elections are active and you've paid your dues, you can vote by going to the
                Elections page, selecting an active election, and clicking "Vote Now." You'll see
                all positions and candidates. Select your preferred candidate for each position and
                submit your votes. Your votes are anonymous and secure.
              </dd>
            </div>

            <div>
              <dt class="text-lg font-medium text-gray-900">
                Can I change my vote after submitting?
              </dt>
              <dd class="mt-2 text-gray-600">
                No, votes are final once submitted. This ensures the integrity and security of the
                election process. Please review your selections carefully before submitting your
                votes.
              </dd>
            </div>

            <div>
              <dt class="text-lg font-medium text-gray-900">How can I make a donation to GMSA?</dt>
              <dd class="mt-2 text-gray-600">
                You can make donations through the Payment section. Select "Make Donation," enter
                your desired amount, and complete the payment. Donations support GMSA activities and
                programs. You can choose to make anonymous donations if you prefer.
              </dd>
            </div>

            <div>
              <dt class="text-lg font-medium text-gray-900">
                When will election results be available?
              </dt>
              <dd class="mt-2 text-gray-600">
                Election results are automatically available once the voting period ends. You can
                view results by going to the Elections page and clicking "View Results" on completed
                elections. Results show vote counts and percentages for all candidates.
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">Contact Information</h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Electoral Commission</h3>
              <div class="space-y-3">
                <div class="flex items-center">
                  <svg
                    class="w-5 h-5 text-gray-400 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                  <span class="text-gray-600">ec@gmsa-university.org</span>
                </div>
                <div class="flex items-center">
                  <svg
                    class="w-5 h-5 text-gray-400 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    />
                  </svg>
                  <span class="text-gray-600">+233 XX XXX XXXX</span>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">Technical Support</h3>
              <div class="space-y-3">
                <div class="flex items-center">
                  <svg
                    class="w-5 h-5 text-gray-400 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                  <span class="text-gray-600">support@gmsa-university.org</span>
                </div>
                <div class="flex items-center">
                  <svg
                    class="w-5 h-5 text-gray-400 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span class="text-gray-600">Available 24/7</span>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8 p-4 bg-green-50 rounded-lg">
            <p class="text-sm text-green-800">
              <strong>Emergency Support:</strong> For urgent issues during active elections, contact
              the Electoral Commission directly via phone or WhatsApp.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// This should match the dues amount from your backend settings
const duesAmount = ref(50)
</script>
