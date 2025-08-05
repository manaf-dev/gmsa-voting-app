<template>
  <Teleport to="body">
    <Transition name="modal-overlay">
      <div
        v-if="show"
        class="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50"
        @click="closeModal"
      >
        <Transition name="modal-content">
          <div
            v-if="show"
            class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col"
            @click.stop
          >
            <!-- Header -->
            <div class="flex-shrink-0 bg-white border-b border-gray-200 p-6 rounded-t-xl">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <User class="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h2 class="text-xl font-bold text-gray-900">
                      {{ candidate?.user?.display_name || 'Candidate' }}
                    </h2>
                    <p class="text-gray-600">{{ candidate?.user?.student_id }}</p>
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
            <div class="flex-1 p-6 overflow-y-auto">
              <div class="space-y-4">
                <!-- Personal Info -->
                <div
                  v-if="
                    candidate?.user?.email ||
                    candidate?.user?.program ||
                    candidate?.user?.year_of_study
                  "
                >
                  <h3 class="text-lg font-semibold text-gray-900 mb-3">Candidate Information</h3>
                  <div class="space-y-2 text-sm">
                    <div v-if="candidate?.user?.email">
                      <span class="text-gray-500">Email:</span>
                      <span class="ml-2 text-gray-800">{{ candidate.user.email }}</span>
                    </div>
                    <div v-if="candidate?.user?.year_of_study">
                      <span class="text-gray-500">Year:</span>
                      <span class="ml-2 text-gray-800">{{ candidate.user.year_of_study }}</span>
                    </div>
                    <div v-if="candidate?.user?.program">
                      <span class="text-gray-500">Program:</span>
                      <span class="ml-2 text-gray-800">{{ candidate.user.program }}</span>
                    </div>
                  </div>
                </div>

                <!-- Manifesto -->
                <div v-if="candidate?.manifesto">
                  <h3 class="text-lg font-semibold text-gray-900 mb-3">Manifesto</h3>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-gray-700 leading-relaxed whitespace-pre-line text-justify">
                      {{ candidate.manifesto }}
                    </p>
                  </div>
                </div>

                <div v-else class="text-center py-8 text-gray-500">
                  <FileText class="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No manifesto provided</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="flex-shrink-0 bg-white border-t border-gray-200 p-6 rounded-b-xl">
              <button
                @click="closeModal"
                class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition"
              >
                Close & Continue Voting
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { User, X, FileText } from 'lucide-vue-next'

interface Props {
  show: boolean
  candidate: any
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const closeModal = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay-enter-active,
.modal-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.modal-overlay-enter-from,
.modal-overlay-leave-to {
  opacity: 0;
}

.modal-content-enter-active,
.modal-content-leave-active {
  transition: all 0.3s ease;
}

.modal-content-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.modal-content-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
</style>
