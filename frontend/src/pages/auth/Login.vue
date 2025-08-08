<script setup lang="ts">
import { ArrowBigLeft } from 'lucide-vue-next'
import BaseBtn from '@/components/BaseBtn.vue'
import { reactive } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from 'vue-toastification'

const toast = useToast()
const authStore = useAuthStore()

const UserDetails = reactive({
  username: '',
  password: '',
})

const SubmitUserDetails = async () => {
  try {
    console.log(UserDetails)
    await authStore.login(UserDetails)
    toast.success('Login successful!')
  } catch (error) {
    toast.error('Invalid credentials')
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-4 text-center">
      <div class="mx-auto w-max">
        <BaseBtn
          class="flex items-center gap-1 text-green-300 hover:bg-green-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowBigLeft /> Back
        </BaseBtn>
      </div>
      <div class="mb-4">
        <h1 class="text-3xl font-bold text-primary-600">AAMUSTED GMSA</h1>
        <p class="text-sm text-gray-600">Ghana Muslim Students Association</p>
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
            <input
              v-model="UserDetails.password"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              placeholder="Enter your password"
            />
          </label>

          <BaseBtn
            class="w-full btn btn-primary py-3 mt-5 flex items-center justify-center cursor-pointer"
          >
            Login
          </BaseBtn>

          <div class="mt-5 text-center">
            <p class="text-sm text-gray-600">
              Don't have an account?
              <router-link
                to="register"
                class="font-medium text-primary-600 hover:text-primary-500"
              >
                Register here
              </router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
