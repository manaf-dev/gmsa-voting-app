<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  totalMembers: 0,
  activeElections: 0,
  totalVotes: 0,
})

const features = [
  {
    icon: 'vote',
    title: 'Secure Voting',
    description: 'Cast your votes securely in GMSA elections with our tamper-proof system',
  },
  {
    icon: 'payment',
    title: 'Easy Payments',
    description: 'Pay your annual dues and make donations using multiple payment methods',
  },
  {
    icon: 'admin',
    title: 'Election Management',
    description: 'EC members can create and manage elections with comprehensive controls',
  },
  {
    icon: 'results',
    title: 'Real-time Results',
    description: 'View election results and statistics as they unfold',
  },
]

onMounted(() => {
  // Mock stats for now - these would come from API
  stats.value = {
    totalMembers: 1250,
    activeElections: 2,
    totalVotes: 892,
  }
})

const navigateToAuth = (route: string) => {
  router.push(route)
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
    <!-- Navigation -->
    <nav class="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-2xl font-bold text-primary-600">GMSA</h1>
            </div>
            <div class="ml-4">
              <span class="text-sm text-gray-600">Ghana Muslim Students Association</span>
            </div>
          </div>

          <div class="flex items-center space-x-4">
              <router-link to="/login" class="btn btn-outline px-4 py-2">Login</router-link>
              <!-- <router-link to="/dashboard" class="btn btn-primary px-4 py-2">
                Dashboard
              </router-link>
              <button
                @click="(authStore.logout(), router.push('/'))"
                class="btn btn-outline px-4 py-2"
              >
                Logout
              </button> -->
          </div>

          <!-- <template v-else>
              <router-link to="/dashboard" class="btn btn-primary px-4 py-2">
                Dashboard
              </router-link>
            </template> -->
          <!-- </div> -->
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto text-center">
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Democratic Elections for
          <span class="text-primary-600"> GMSA</span>
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Secure, transparent, and accessible voting platform for the Ghana Muslim Students
          Association. Make your voice heard in shaping our community's future.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <template>
            <router-link to="/register" class="btn btn-primary px-8 py-3 text-lg">
              Join GMSA Today
            </router-link>
            <router-link to="/login" class="btn btn-outline px-8 py-3 text-lg">
              Already a Member?
            </router-link>
          </template>
          <template>
            <router-link to="/elections" class="btn btn-primary px-8 py-3 text-lg">
              View Elections
            </router-link>
            <router-link to="/dashboard" class="btn btn-outline px-8 py-3 text-lg">
              My Dashboard
            </router-link>
          </template>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 bg-white/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div
              class="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-primary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                />
              </svg>
            </div>
            <h3 class="text-3xl font-bold text-gray-900">
              {{ stats.totalMembers.toLocaleString() }}
            </h3>
            <p class="text-gray-600">Registered Members</p>
          </div>

          <div class="text-center">
            <div
              class="bg-secondary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-secondary-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 class="text-3xl font-bold text-gray-900">{{ stats.activeElections }}</h3>
            <p class="text-gray-600">Active Elections</p>
          </div>

          <div class="text-center">
            <div
              class="bg-accent-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4"
            >
              <svg
                class="w-8 h-8 text-accent-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"
                />
              </svg>
            </div>
            <h3 class="text-3xl font-bold text-gray-900">
              {{ stats.totalVotes.toLocaleString() }}
            </h3>
            <p class="text-gray-600">Votes Cast</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Why Choose Our Platform?</h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Built with security, transparency, and accessibility in mind
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div class="text-center">
            <div class="bg-primary-100 rounded-lg p-6 mb-4">
              <svg
                class="w-12 h-12 text-primary-600 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Secure Voting</h3>
            <p class="text-gray-600">
              End-to-end encryption ensures your vote remains private and secure
            </p>
          </div>

          <div class="text-center">
            <div class="bg-secondary-100 rounded-lg p-6 mb-4">
              <svg
                class="w-12 h-12 text-secondary-600 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Transparent Process</h3>
            <p class="text-gray-600">
              Real-time results and complete audit trails for full transparency
            </p>
          </div>

          <div class="text-center">
            <div class="bg-accent-100 rounded-lg p-6 mb-4">
              <svg
                class="w-12 h-12 text-accent-600 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Mobile Friendly</h3>
            <p class="text-gray-600">Vote from anywhere using your smartphone or computer</p>
          </div>

          <div class="text-center">
            <div class="bg-primary-100 rounded-lg p-6 mb-4">
              <svg
                class="w-12 h-12 text-primary-600 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Easy Payments</h3>
            <p class="text-gray-600">Secure dues payment and donation system integrated</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-primary-600">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl font-bold text-white mb-4">Ready to Make Your Voice Heard?</h2>
        <p class="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
          Join thousands of GMSA members who are actively participating in shaping our community's
          future.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <template>
            <router-link
              to="/register"
              class="bg-white text-primary-600 hover:bg-gray-50 px-8 py-3 rounded-md font-semibold transition-colors"
            >
              Get Started Today
            </router-link>
            <router-link
              to="/payment/donation"
              class="border border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 rounded-md font-semibold transition-colors"
            >
              Support GMSA
            </router-link>
          </template>
          <template>
            <router-link
              to="/elections"
              class="bg-white text-primary-600 hover:bg-gray-50 px-8 py-3 rounded-md font-semibold transition-colors"
            >
              View Elections
            </router-link>
            <router-link
              to="/payment/donation"
              class="border border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 rounded-md font-semibold transition-colors"
            >
              Make a Donation
            </router-link>
          </template>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-2xl font-bold mb-4">GMSA</h3>
            <p class="text-gray-400">
              Ghana Muslim Students Association - Building unity, fostering growth, and empowering
              voices in our community.
            </p>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Quick Links</h4>
            <ul class="space-y-2 text-gray-400">
              <li>
                <router-link to="/elections" class="hover:text-white transition-colors"
                  >Elections</router-link
                >
              </li>
              <li>
                <router-link to="/payment/dues" class="hover:text-white transition-colors"
                  >Pay Dues</router-link
                >
              </li>
              <li>
                <router-link to="/payment/donation" class="hover:text-white transition-colors"
                  >Donate</router-link
                >
              </li>
            </ul>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Contact</h4>
            <p class="text-gray-400">
              Email: info@gmsa.edu.gh<br />
              Phone: +233 XX XXX XXXX
            </p>
          </div>
        </div>

        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 Ghana Muslim Students Association. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>
