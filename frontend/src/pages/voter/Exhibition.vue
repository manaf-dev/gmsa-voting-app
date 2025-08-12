<template>
  <div
    class="relative min-h-screen flex items-start md:items-center justify-center overflow-hidden"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-emerald-50 via-white to-emerald-100"></div>
    <div
      class="pointer-events-none absolute -top-32 -left-32 w-96 h-96 rounded-full bg-emerald-200/30 blur-3xl"
    ></div>
    <div
      class="pointer-events-none absolute bottom-0 -right-20 w-[32rem] h-[32rem] rounded-full bg-green-300/20 blur-3xl"
    ></div>

    <div class="relative w-full max-w-2xl mx-auto p-4 sm:p-6">
      <div class="mb-8 text-center">
        <h1
          class="text-3xl md:text-4xl font-bold tracking-tight bg-gradient-to-r from-emerald-600 to-green-700 bg-clip-text text-transparent"
        >
          Voter Register Exhibition
        </h1>
        <p class="mt-3 text-sm md:text-base text-gray-600 max-w-md mx-auto">
          Verify your presence on the GMSA voter register. If you're not listed, submit your details
          for verification.
        </p>
      </div>

      <transition name="fade-slide" mode="out-in">
        <!-- Lookup Step -->
        <div
          v-if="step === 'lookup'"
          key="lookup"
          class="bg-white/80 backdrop-blur rounded-xl shadow-sm border border-emerald-100 p-6 space-y-5"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-9 h-9 flex items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-semibold"
            >
              1
            </div>
            <h2 class="text-lg font-semibold text-emerald-800">Search Register</h2>
          </div>
          <form @submit.prevent="handleLookup" class="space-y-4">
            <div>
              <label class="form-label">Phone Number</label>
              <div class="relative">
                <input
                  v-model="phone"
                  type="tel"
                  required
                  placeholder="0XXXXXXXXX"
                  maxlength="10"
                  class="form-input form-input-lg pr-10"
                  :class="{ 'input-error': error }"
                />
                <button
                  v-if="phone"
                  type="button"
                  @click="
                    phone = ''
                    // error = ''
                  "
                  class="clear-btn"
                >
                  &times;
                </button>
              </div>
              <p class="hint">Ghana local format (10 digits). We'll auto-normalize +233 formats.</p>
            </div>
            <button :disabled="loading" class="btn-primary">
              <span class="relative flex items-center justify-center gap-2">
                <svg
                  v-if="loading"
                  class="animate-spin h-4 w-4 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" />
                  <path class="opacity-75" d="M4 12a8 8 0 018-8" />
                </svg>
                <span>{{ loading ? 'Checking...' : 'Search Register' }}</span>
              </span>
            </button>
            <p
              v-if="error"
              class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded border border-red-100"
            >
              {{ error }}
            </p>
          </form>
        </div>

        <!-- Found -->
        <div
          v-else-if="step === 'found'"
          key="found"
          class="bg-white/85 backdrop-blur rounded-xl shadow p-6 text-center space-y-6 border border-emerald-200"
        >
          <div class="flex flex-col items-center gap-3">
            <div class="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center">
              <svg
                class="w-7 h-7 text-emerald-600"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-xl font-semibold text-emerald-700">Record Located</h2>
            <p class="text-sm text-gray-600 max-w-sm">
              Your phone number matches an existing voter record. (Details hidden for privacy.)
            </p>
          </div>
          <button
            @click="reset"
            class="text-sm font-medium text-emerald-700 hover:text-emerald-800 underline"
          >
            Search another number
          </button>
        </div>

        <!-- Register -->
        <div
          v-else-if="step === 'register'"
          key="register"
          class="bg-white/85 backdrop-blur rounded-xl shadow-sm border border-emerald-100 p-6 space-y-6"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-9 h-9 flex items-center justify-center rounded-full bg-emerald-100 text-emerald-700 font-semibold"
            >
              2
            </div>
            <h2 class="text-lg font-semibold text-emerald-800">Submit Your Details</h2>
          </div>
          <div class="text-sm bg-amber-50 text-amber-700 px-3 py-2 rounded border border-amber-200">
            No record found. Provide accurate information for verification.
          </div>
          <form @submit.prevent="handleRegister" class="space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="col-span-1">
                <label class="form-label">First Name<span class="text-red-500">*</span></label>
                <input v-model="form.first_name" required class="form-input form-input-lg" />
              </div>
              <div class="col-span-1">
                <label class="form-label">Last Name<span class="text-red-500">*</span></label>
                <input v-model="form.last_name" required class="form-input form-input-lg" />
              </div>
              <div class="col-span-1 md:col-span-2">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" disabled class="form-input form-input-lg bg-gray-50" />
              </div>
              <div>
                <label class="form-label">Student ID (optional)</label>
                <input v-model="form.student_id" class="form-input form-input-lg" />
              </div>
              <div>
                <label class="form-label">Program (optional)</label>
                <input v-model="form.program" class="form-input form-input-lg" />
              </div>
              <div>
                <label class="form-label">Year of Study (optional)</label>
                <select v-model="form.year_of_study" class="form-input form-input-lg">
                  <option value="">Select Year</option>
                  <option value="100">Level 100</option>
                  <option value="200">Level 200</option>
                  <option value="300">Level 300</option>
                  <option value="400">Level 400</option>
                </select>
              </div>
            </div>
            <div class="space-y-3">
              <button :disabled="loading" class="btn-primary">
                <svg
                  v-if="loading"
                  class="animate-spin h-4 w-4 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10" class="opacity-25" />
                  <path d="M4 12a8 8 0 018-8" class="opacity-75" />
                </svg>
                <span>{{ loading ? 'Submitting...' : 'Submit for Verification' }}</span>
              </button>
              <p
                v-if="error"
                class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded border border-red-100"
              >
                {{ error }}
              </p>
              <button type="button" @click="reset" class="btn-link">Start over</button>
            </div>
          </form>
        </div>

        <!-- Submitted -->
        <div
          v-else-if="step === 'submitted'"
          key="submitted"
          class="bg-white/85 backdrop-blur rounded-xl shadow p-6 text-center space-y-6 border border-emerald-200"
        >
          <div class="flex flex-col items-center gap-3">
            <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center">
              <svg
                class="w-7 h-7 text-green-600"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-xl font-semibold text-green-700">Submission Received</h2>
            <p class="text-sm text-gray-600 max-w-sm">
              Your details have been queued for manual verification. You'll be added to the register
              once approved.
            </p>
          </div>
          <button
            @click="reset"
            class="text-sm font-medium text-emerald-700 hover:text-emerald-800 underline"
          >
            Search another number
          </button>
        </div>
      </transition>

      <!-- Footer note -->
      <p class="mt-10 text-[11px] tracking-wide text-center text-gray-500">
        Data is used solely for election eligibility verification • GMSA EC
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { exhibitionLookup, exhibitionRegister } from '@/services/exhibition'

const step = ref<'lookup' | 'found' | 'register' | 'submitted'>('lookup')
const phone = ref('')
const loading = ref(false)
const error = ref('')

const form = ref({
  phone: '',
  first_name: '',
  last_name: '',
  student_id: '',
  program: '',
  year_of_study: '',
})

function normalizePhone(input: string) {
  let digits = input.replace(/\D/g, '')
  if (digits.startsWith('233') && digits.length >= 12) {
    digits = '0' + digits.slice(3, 12)
  } else if (digits.length === 9) {
    digits = '0' + digits
  }
  return digits
}

async function handleLookup() {
  error.value = ''
  loading.value = true
  try {
    const normalized = normalizePhone(phone.value)
    phone.value = normalized
    const res = await exhibitionLookup(normalized)
    if (res.status === 'found') {
      step.value = 'found'
    } else {
      form.value.phone = normalized
      step.value = 'register'
    }
  } catch (e: any) {
    error.value = e?.response?.data?.phone?.[0] || e?.response?.data?.detail || 'Lookup failed'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    form.value.phone = normalizePhone(form.value.phone || phone.value)
    const res = await exhibitionRegister(form.value)
    if (res.status === 'created' || res.status === 'exists') {
      step.value = res.status === 'exists' ? 'found' : 'submitted'
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}

function reset() {
  step.value = 'lookup'
  phone.value = ''
  form.value = {
    phone: '',
    first_name: '',
    last_name: '',
    student_id: '',
    program: '',
    year_of_study: '',
  }
  error.value = ''
}
</script>

<style scoped>
.form-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #374151;
  margin-bottom: 0.3rem;
  display: block;
}
.form-input {
  width: 100%;
  border: 2px solid #bbf7d0;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 0.65rem;
  padding: 0.9rem 1rem;
  font-size: 1rem;
  line-height: 1.2;
  box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}
.form-input:focus {
  outline: none;
  background: #fff;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.35);
}
.form-input[disabled] {
  background: #f1f5f9;
  opacity: 0.85;
  cursor: not-allowed;
}
.form-input-lg {
  padding: 1rem 1.1rem;
  font-size: 1.05rem;
}
.input-error {
  border-color: #f87171 !important;
  box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.35) !important;
}
.hint {
  margin-top: 0.4rem;
  font-size: 0.7rem;
  color: #64748b;
}
.btn-primary {
  width: 100%;
  border: none;
  background: linear-gradient(90deg, #059669, #047857);
  color: #fff;
  font-weight: 600;
  padding: 1rem 1.2rem;
  border-radius: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  font-size: 1rem;
  letter-spacing: 0.25px;
  box-shadow: 0 6px 18px -4px rgba(16, 185, 129, 0.45);
  transition: all 0.22s ease;
}
.btn-primary:hover:not(:disabled) {
  filter: brightness(1.05);
  box-shadow: 0 8px 22px -6px rgba(16, 185, 129, 0.55);
}
.btn-primary:active {
  transform: translateY(1px);
}
.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.btn-link {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.8rem;
  color: #03624c;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 500;
}
.btn-link:hover {
  color: #024c3b;
}
.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: #e2f7ec;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 9999px;
  font-size: 18px;
  line-height: 1;
  color: #047857;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
}
.clear-btn:hover {
  background: #c1f1da;
  color: #035c44;
}
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
