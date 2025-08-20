<script setup lang="ts">
import { ArrowBigLeft, Eye, EyeOff } from 'lucide-vue-next'
import BaseBtn from '@/components/BaseBtn.vue'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from 'vue-toastification'

const toast = useToast()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const UserDetails = reactive({
  username: '',
  password: '',
})

const showPassword = ref(false)

const loading = ref(false)

const SubmitUserDetails = async () => {
  if (loading.value) return
  loading.value = true
  try {
  const redirectTo = (route.query.redirect as string) || '/dashboard'
  await authStore.login(UserDetails, redirectTo)
    toast.success('Login successful!')
  } catch (error) {
    toast.error('Invalid credentials')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-4 text-center">
      <!-- <div class="mx-auto w-max">
        <BaseBtn
          class="flex items-center gap-1 text-green-300 hover:bg-green-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowBigLeft /> Back
        </BaseBtn>
      </div> -->
      <div class="mb-4">
        <h1 class="text-3xl font-bold text-primary-600">AAMUSTED BESA</h1>
        <p class="text-sm text-gray-600">Basic Education Students Association</p>
      </div>

      <!--Form-->
      <div class="bg-white rounded-xl shadow-xl p-8">
        <form @submit.prevent="SubmitUserDetails">
          <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
            Username or Student ID
            <input
              v-model="UserDetails.username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              placeholder="Enter your username or student ID"
            />
          </label>

          <label class="block text-sm font-medium text-gray-700 mb-2 text-left">
            Password
            <div class="relative mt-1">
              <input
                v-model="UserDetails.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                class="w-full pr-11 px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your password"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <EyeOff v-if="showPassword" class="h-5 w-5" />
                <Eye v-else class="h-5 w-5" />
              </button>
            </div>
          </label>

          <BaseBtn
            :disabled="loading"
            class="w-full btn btn-primary py-3 mt-5 flex items-center justify-center cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed gap-2"
          >
            <svg
              v-if="loading"
              class="animate-spin h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>{{ loading ? 'Signing in...' : 'Login' }}</span>
          </BaseBtn>

          <!-- <div class="mt-5 text-center">
            <p class="text-sm text-gray-600">
              Don't have an account?
              <router-link
                to="register"
                class="font-medium text-primary-600 hover:text-primary-500"
              >
                Register here
              </router-link>
            </p>
          </div> -->
        </form>
      </div>
    </div>
  </div>
</template>
