<script setup lang="ts">
import { ArrowLeft, CheckCircle, Printer } from 'lucide-vue-next'
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<any>(null)

const election = computed(() => data.value?.election || {})
const positions = computed(() => data.value?.positions || [])

const fetchResults = async () => {
  try {
    loading.value = true
    const resp = await api.get(`/elections/${id}/results/`)
    data.value = resp.data
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Failed to load results'
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()

onMounted(fetchResults)

const publish = async () => {
  try {
    loading.value = true
    await api.post(`/elections/${id}/publish/`)
    await fetchResults()
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Failed to publish results'
  } finally {
    loading.value = false
  }
}

const archive = async () => {
  try {
    loading.value = true
    await api.post(`/elections/${id}/archive/`)
    await fetchResults()
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Failed to archive election'
  } finally {
    loading.value = false
  }
}

const fmt12h = (d?: string | Date) => {
  if (!d) return '-'
  const date = new Date(d)
  const datePart = date.toLocaleDateString()
  const timePart = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
  return `${datePart} ${timePart}`
}

const printPage = () => {
  window.print()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white/80 border-b border-gray-200">
      <div
        class="max-w-6xl mx-auto w-full flex items-center justify-between px-4 lg:px-8 py-3 md:py-5"
      >
        <button
          @click="goBack"
          class="block transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowLeft />
        </button>
        <h1 class="text-xl font-bold">{{ election.title || 'Election Results' }}</h1>
        <div>
          <span class="text-xs py-2 px-3 text-purple-800 bg-purple-100 rounded-full">{{
            election.status
          }}</span>
        </div>
      </div>
    </nav>

    <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        <p class="mt-4 text-gray-500">Loading results...</p>
      </div>
      <div v-else-if="error" class="text-center py-12">
        <p class="text-gray-600">{{ error }}</p>
      </div>
      <template v-else>
        <!-- Header -->
        <div class="bg-white rounded-lg shadow p-6 text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ election.title }}</h1>
          <p class="text-gray-600 mb-4" v-if="election.results_published">
            Official results have been published.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Election Period:</span>
              <span class="font-medium block"
                >{{ fmt12h(election.start_date) }} - {{ fmt12h(election.end_date) }}</span
              >
            </div>
            <div>
              <span class="text-gray-500">Eligible Voters:</span>
              <span class="font-medium block">{{ election.total_eligible_voters }}</span>
            </div>
            <div>
              <span class="text-gray-500">Participated:</span>
              <span class="font-medium block">{{ election.total_voters }}</span>
            </div>
            <div>
              <span class="text-gray-500">Turnout:</span>
              <span class="font-medium block"
                >{{ (election.voter_turnout_percentage || 0).toFixed(1) }}%</span
              >
            </div>
            <div>
              <span class="text-gray-500">Total Votes Cast:</span>
              <span class="font-medium block">{{ election.total_votes }}</span>
            </div>
            <div v-if="election.results_published">
              <span class="text-gray-500">Published At:</span>
              <span class="font-medium block">{{ fmt12h(election.results_published_at) }}</span>
            </div>
          </div>
          <div class="mt-4 flex items-center justify-center gap-2">
            <button
              v-if="election.can_review_results && !election.results_published"
              @click="publish"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md"
            >
              Publish Results
            </button>
            <button
              v-if="election.can_archive"
              @click="archive"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
            >
              Archive
            </button>
            <button
              @click="printPage"
              class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-md inline-flex items-center gap-2"
            >
              <Printer class="w-4 h-4" /> Print / Save PDF
            </button>
          </div>
        </div>
        <!-- Results by Position -->
        <div class="space-y-6 mt-5">
          <div
            v-if="positions.length === 0"
            class="bg-white rounded-lg shadow p-6 text-center text-gray-500"
          >
            No positions or candidates to display.
          </div>
          <div v-for="pos in positions" :key="pos.id" class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex justify-between">
                <div>
                  <h3 class="text-xl font-semibold text-gray-900">{{ pos.title }}</h3>
                </div>
                <p class="text-sm text-gray-500 text-right">Total Votes: {{ pos.total_votes }}</p>
              </div>
            </div>

            <div class="p-6 space-y-4">
              <div v-if="pos.candidates?.length === 0" class="text-sm text-gray-500">
                No candidates.
              </div>
              <div v-else>
                <div
                  v-for="(c, idx) in pos.candidates"
                  :key="c.id"
                  :class="[
                    'border rounded-lg p-4',
                    idx === 0 ? 'border-green-300 bg-green-50' : 'border-gray-200',
                  ]"
                >
                  <div class="flex justify-between">
                    <div class="flex items-center space-x-4">
                      <div class="w-8 h-8" />
                      <div
                        class="w-12 h-12 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center"
                      >
                        <img
                          v-if="c.profile_picture_url"
                          :src="c.profile_picture_url"
                          alt=""
                          class="w-12 h-12 object-cover"
                        />
                        <span v-else class="text-primary-600 font-medium">{{
                          (c.name || '')[0]
                        }}</span>
                      </div>
                      <div>
                        <h4 class="font-semibold text-gray-900 flex items-center">
                          {{ c.name }}
                          <CheckCircle v-if="idx === 0" class="w-5 h-5 text-green-600 ml-2" />
                        </h4>
                        <span class="text-sm text-gray-600">{{ c.student_id }}</span>
                      </div>
                    </div>
                    <div class="text-right">
                      <span class="text-2xl font-bold text-gray-900">{{ c.vote_count }}</span>
                      <span class="text-sm text-gray-500">{{ c.vote_percentage }}%</span>
                    </div>
                  </div>
                  <div class="mt-4">
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="h-2 rounded-full bg-green-600"
                        :style="{ width: `${c.vote_percentage}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div
                  v-if="pos.yes_count !== undefined && pos.no_count !== undefined"
                  class="mt-2 text-sm text-gray-700"
                >
                  YES: <span class="font-medium text-green-700">{{ pos.yes_count }}</span> · NO:
                  <span class="font-medium text-red-700">{{ pos.no_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-5">
          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-blue-600 mb-2">{{ positions.length }}</div>
            <div class="text-gray-600">Positions Contested</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-green-600 mb-2">{{ election.total_votes }}</div>
            <div class="text-gray-600">Total Votes Cast</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6 text-center">
            <div class="text-3xl font-bold text-purple-600 mb-2">{{ election.total_voters }}</div>
            <div class="text-gray-600">Voters Participated</div>
          </div>
        </div>

        <!-- Winner Announcement (optional, highlight top candidate per position) -->
        <div class="bg-gray-900 rounded-lg shadow text-white p-8 mt-5">
          <div class="text-center">
            <h2 class="text-2xl font-bold mb-6">Highlights</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="pos in positions"
                :key="pos.id"
                class="bg-white/10 backdrop-blur-sm rounded-lg p-4"
              >
                <h3 class="font-semibold mb-2">{{ pos.title }}</h3>
                <p class="text-lg font-bold">{{ pos.candidates?.[0]?.name || '—' }}</p>
                <p class="text-sm opacity-90">
                  {{ pos.candidates?.[0]?.vote_count || 0 }} votes ({{
                    pos.candidates?.[0]?.vote_percentage || 0
                  }}%)
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style>
@media print {
  nav,
  .router-link,
  .router-link-active,
  button {
    display: none !important;
  }
  .bg-white {
    box-shadow: none !important;
  }
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
