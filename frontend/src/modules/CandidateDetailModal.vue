<script setup lang="ts">
import { computed } from 'vue'
import { X, User, Mail, Calendar, BookOpen, FileText } from 'lucide-vue-next'

interface Props {
  show: boolean
  candidate: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const closeModal = () => {
  emit('close')
}

// Handle escape key
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Add/remove event listener when modal opens/closes
const handleModalVisibility = () => {
  if (props.show) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'auto'
  }
}

// Watch for show prop changes
import { watch } from 'vue'
watch(() => props.show, handleModalVisibility, { immediate: true })

const candidateInfo = computed(() => {
  if (!props.candidate) return null

  return {
    name: props.candidate.user?.display_name || 'Name N/A',
    studentId: props.candidate.user?.student_id || 'ID N/A',
    email: props.candidate.user?.email || 'Email N/A',
    year: props.candidate.user?.year_of_study || 'Year N/A',
    program: props.candidate.user?.program || 'Program N/A',
    manifesto: props.candidate.manifesto || 'No manifesto provided',
    voteCount: props.candidate.vote_count || 0,
    dateJoined: props.candidate.user?.date_joined || null,
    profile_url: props.candidate.profile_picture
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
        @click.self="closeModal"
      >
        <Transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-300"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="show && candidateInfo"
            class="bg-white rounded-xl shadow-2xl max-w-xl w-full max-h-[85vh] overflow-y-auto border border-gray-200 ring-1 ring-black ring-opacity-5"
          >
            <!-- Header -->
            <div class="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-xl">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center">
                      <img v-if="candidateInfo.profile_url" :src="candidateInfo.profile_url" alt="" class="w-12 h-12 object-cover" />
                      <span v-else class="text-primary-600 font-medium">CA</span>
                  </div>
                  <div>
                    <h2 class="text-2xl font-bold text-gray-900">
                      {{ candidateInfo.name }}
                    </h2>
                    <p class="text-gray-600">{{ candidateInfo.studentId }}</p>
                  </div>
                </div>
                <button
                  @click="closeModal"
                  class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition"
                >
                  <X class="h-6 w-6" />
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="p-6 space-y-6">
              <!-- Personal Information -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <User class="h-5 w-5 text-gray-600" />
                  Personal Information
                </h3>
                <div class="space-y-3">
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <Mail class="h-4 w-4 text-gray-500" />
                      <span class="text-sm font-medium text-gray-600">Email</span>
                    </div>
                    <p class="text-sm text-gray-800 break-all">{{ candidateInfo.email }}</p>
                  </div>
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <Calendar class="h-4 w-4 text-gray-500" />
                      <span class="text-sm font-medium text-gray-600">Year of Study</span>
                    </div>
                    <p class="text-sm text-gray-800">{{ candidateInfo.year }}</p>
                  </div>
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <BookOpen class="h-4 w-4 text-gray-500" />
                      <span class="text-sm font-medium text-gray-600">Program</span>
                    </div>
                    <p class="text-sm text-gray-800 break-words">{{ candidateInfo.program }}</p>
                  </div>
                </div>
              </div>

              <!-- Manifesto -->
              <!-- <div class="bg-white border border-gray-200 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FileText class="h-5 w-5 text-gray-600" />
                  Manifesto
                </h3>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {{ candidateInfo.manifesto }}
                  </p>
                </div>
              </div> -->

              <!-- Additional Information
              <div v-if="candidateInfo.dateJoined" class="bg-blue-50 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Calendar class="h-5 w-5 text-gray-600" />
                  Additional Information
                </h3>
                <p class="text-sm text-gray-600">
                  Member since: {{ new Date(candidateInfo.dateJoined).toLocaleDateString() }}
                </p>
              </div> -->
            </div>

            <!-- Footer -->
            <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 rounded-b-xl">
              <div class="flex justify-end">
                <button
                  @click="closeModal"
                  class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.prose {
  color: inherit;
}
.prose p {
  margin-bottom: 1em;
}
.prose p:last-child {
  margin-bottom: 0;
}
</style>
