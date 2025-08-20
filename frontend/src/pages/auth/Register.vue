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
  first_name: '',
  last_name: '',
  student_id: '',
  phone_number: '',
  year_of_study: '',
  program: '',
  admission_year: '',
  password: '',
  confirm_password: '',
})

const SubmitUserDetails = async () => {
  try {
    await authStore.register(UserDetails)
    toast.success('Registration successful!')
  } catch (error) {
    toast.error('Invalid credentials or registration failed')
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full space-y-4">
      <div class="mx-auto w-max">
        <BaseBtn
          class="flex items-center gap-1 text-green-300 hover:bg-green-50 hover:gap-1.5 transition-all ease-in-out duration-200 py-1 px-3 rounded-full cursor-pointer"
        >
          <ArrowBigLeft /> Back
        </BaseBtn>
      </div>
      <div class="mb-4 text-center">
        <h1 class="text-3xl font-bold text-primary-600">AAMUSTED BESA</h1>
        <p class="text-sm text-gray-600">Basic Education Students Association</p>
      </div>

      <!--Form-->
      <div>
        <form @submit.prevent="SubmitUserDetails" class="bg-white rounded-xl shadow-xl p-4 sm:p-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <label class="block text-sm font-medium text-gray-700">
              First Name <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.first_name"
                type="text"
                required
                autocomplete="firstname"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your first name"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Last Name <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.last_name"
                type="text"
                required
                autocomplete="lastname"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your last name"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              User Name <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.username"
                type="text"
                required
                autocomplete="username"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your username"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Student ID <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.student_id"
                type="text"
                required
                autocomplete="student-id"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your student ID"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Phone Number <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.phone_number"
                type="tel"
                required
                autocomplete="tel"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your phone number"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Program of Study <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.program"
                type="text"
                required
                autocomplete="program"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your program"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Year of Study <span class="text-orange-500">*</span>
              <select
                v-model="UserDetails.year_of_study"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              >
                <option disabled>Select year</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="300">300</option>
                <option value="400">400</option>
              </select>
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Admission Year <span class="text-orange-500">*</span>
              <select
                v-model="UserDetails.admission_year"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
              >
                <option disabled>Select year</option>
                <option value="2023">2023</option>
                <option value="2024">2024</option>
                <option value="2025">2025</option>
              </select>
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Password <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.password"
                type="password"
                required
                autocomplete="new-password"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Enter your password"
              />
            </label>

            <label class="block text-sm font-medium text-gray-700">
              Confirm Password <span class="text-orange-500">*</span>
              <input
                v-model="UserDetails.confirm_password"
                type="password"
                required
                autocomplete="new-password"
                class="w-full px-3 py-2 border mt-1 border-gray-300 rounded-lg placeholder-gray-400 outline-none focus:ring-2 ring-gray-500"
                placeholder="Confirm your password"
              />
            </label>
          </div>

          <BaseBtn
            class="w-full btn btn-primary py-3 mt-5 flex items-center justify-center cursor-pointer"
          >
            Login
          </BaseBtn>

          <div class="mt-5 text-center">
            <p class="text-sm text-gray-600">
              Already have an account?
              <router-link to="login" class="font-medium text-green-600 hover:text-green-500">
                Sign In
              </router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
