<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// Attempt to load the BESA logo asset
let logoSrc: string | undefined
try {
  // @ts-ignore - Vite will resolve at runtime if recognized as an asset
  logoSrc = new URL('@/assets/BESA_LOGO.jpeg', import.meta.url).href
} catch (e) {
  logoSrc = ''
}

const primaryActions = [
  { label: 'Login', to: '/login', style: 'bg-green-600 hover:bg-green-700 text-white' },
  { label: 'Donate to BESA', to: '/payment/donation', style: 'bg-white/10 hover:bg-white/20 text-white border border-white/30 backdrop-blur' },
]

const pillars = [
  { title: 'Excellence', body: 'Promoting academic achievement and educational advancement.' },
  { title: 'Service', body: 'Community impact through outreach, support and mentorship.' },
  { title: 'Leadership', body: 'Building capable, visionary student leaders for tomorrow.' },
]

const go = (to: string) => router.push(to)
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-b from-green-50 via-white to-white">
    <!-- Minimal Nav -->
    <header class="w-full">
      <div class="max-w-6xl mx-auto flex items-center justify-between px-5 py-3 sm:py-4">
        <div class="flex items-center gap-3">
          <div class="relative h-11 w-11 flex items-center justify-center">
            <img v-if="logoSrc" :src="logoSrc" alt="BESA Logo" class="h-11 w-11 object-contain drop-shadow" />
            <div v-else class="h-11 w-11 rounded-lg bg-green-600 text-white flex items-center justify-center font-bold text-lg">B</div>
          </div>
            <div class="leading-tight">
              <p class="font-semibold text-gray-800 text-sm sm:text-base">AAMUSTED BESA</p>
              <p class="text-[10px] sm:text-[11px] text-gray-500 tracking-wide uppercase">Basic Education Students Association</p>
            </div>
        </div>
        <nav class="flex items-center gap-2 sm:gap-3">
          <router-link to="/login" class="px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium text-gray-700 hover:text-white hover:bg-green-600 transition-colors">Login</router-link>
          <!-- <router-link to="/" class="px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium bg-green-600 text-white hover:bg-green-700 shadow-sm transition-colors">Donate</router-link> -->
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <main class="flex-1">
      <section class="relative px-6 pt-10 pb-16 sm:pt-16 sm:pb-20 overflow-hidden">
        <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
          <div class="absolute -top-24 -right-16 h-72 w-72 bg-green-100 rounded-full blur-3xl opacity-60"></div>
          <div class="absolute top-1/3 -left-20 h-64 w-64 bg-emerald-100 rounded-full blur-3xl opacity-50"></div>
        </div>
        <div class="relative max-w-4xl mx-auto text-center">
          <h1 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-gray-900">
            BESA <span class="text-green-600">goes to the polls</span>
          </h1>
          <p class="mt-4 text-gray-600 text-sm sm:text-lg leading-relaxed max-w-2xl mx-auto">
            A dedicated student community committed to academic excellence and
            educational advancement.
          </p>
          <p class="mt-3 text-xs sm:text-sm text-gray-500 max-w-xl mx-auto">
            Together in Knowledge, Growth and Service.
          </p>
          <!-- <div class="mt-9 flex flex-col sm:flex-row gap-3 justify-center">
            <button
              v-for="a in primaryActions"
              :key="a.label"
              @click="go(a.to)"
              class="group px-7 py-3 rounded-lg text-sm sm:text-base font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all backdrop-blur"
              :class="[
                a.to === '/login' ? 'bg-green-600 hover:bg-green-700 text-white shadow-green-600/40' : 'border border-green-500/40 text-green-700 hover:bg-green-600 hover:text-white'
              ]"
            >
              <span class="inline-flex items-center gap-1">
                {{ a.label }}
                <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>
              </span>
            </button>
          </div> -->
        </div>
      </section>

      <!-- Pillars (very short) -->
      <!-- <section class="px-6 pb-14">
        <div class="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-5 sm:gap-6">
          <div v-for="p in pillars" :key="p.title" class="bg-white rounded-xl border border-green-100/70 shadow-sm p-5 text-center hover:shadow-md transition-shadow">
            <h3 class="font-semibold text-gray-900 tracking-wide text-sm uppercase mb-2">{{ p.title }}</h3>
            <p class="text-xs sm:text-sm text-gray-600 leading-relaxed">{{ p.body }}</p>
          </div>
        </div>
      </section> -->
    </main>

    <!-- Compact footer -->
    <footer class="border-t border-gray-200 py-6 text-center text-xs text-gray-500">
      <p>&copy; {{ new Date().getFullYear() }} AAMUSTED BESA. All rights reserved.</p>
    </footer>
  </div>
</template>
