<script setup lang="ts">
import { ref } from 'vue'
import { paymentService } from '@/services/payments'
import api from '@/services/api'

interface DonationForm {
  amount: string
  donor_name: string
  message: string
  is_anonymous: boolean
}

const loading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const paystackKey = ref('')
const reference = ref('')
const showInlineBox = ref(false)

const form = ref<DonationForm>({
  amount: '',
  donor_name: '',
  message: '',
  is_anonymous: true,
})

// Fetch public config
api.get('/payments/config/').then(r => {
  paystackKey.value = r.data.paystack_public_key
}).catch(()=>{})

function validate(): boolean {
  error.value = null
  const amt = parseFloat(form.value.amount)
  if (isNaN(amt) || amt <= 0) {
    error.value = 'Enter a valid amount greater than 0'
    return false
  }
  if (!paystackKey.value) {
    error.value = 'Payment not available. Try again shortly.'
    return false
  }
  return true
}

async function submitDonation() {
  if (!validate()) return
  loading.value = true
  success.value = null
  try {
    const amt = parseFloat(form.value.amount)
    const resp = await paymentService.initiatePayment({
      payment_type: 'donation',
      amount: amt,
      donor_name: form.value.donor_name || undefined,
      message: form.value.message || undefined,
      is_anonymous: form.value.is_anonymous,
    })
    reference.value = resp.reference
    // For now open external checkout; inline custom requires extra verify step after card collection
    paymentService.openPaystackCheckout(resp.authorization_url)
    success.value = 'Redirected to secure checkout. Complete payment to finish.'
  } catch (e: any) {
    error.value = e?.response?.data?.error || 'Failed to start donation'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 via-white to-white py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-green-700">Support AAMUSTED GMSA</h1>
        <p class="mt-2 text-sm text-gray-600">Make a sadaqah / donation to strengthen our programmes.</p>
      </div>

      <div class="bg-white/90 backdrop-blur rounded-2xl shadow-lg border border-green-100 p-6 sm:p-8">
        <form @submit.prevent="submitDonation" class="space-y-6">
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 text-sm p-3 rounded-md">{{ error }}</div>
          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 text-sm p-3 rounded-md">{{ success }}</div>

          <div>
            <label for="amount" class="block text-sm font-medium text-gray-700 mb-1">Amount (GHS) *</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₵</span>
              <input v-model="form.amount" id="amount" type="number" step="0.01" min="1" required class="w-full pl-8 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500/60 focus:border-green-500 shadow-sm" placeholder="50" />
            </div>
          </div>

            <div class="flex items-center">
              <input v-model="form.is_anonymous" id="is_anonymous" type="checkbox" class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded" />
              <label for="is_anonymous" class="ml-2 block text-sm text-gray-700">Give anonymously</label>
            </div>

          <div v-if="!form.is_anonymous">
            <label for="donor_name" class="block text-sm font-medium text-gray-700 mb-1">Name (Optional)</label>
            <input v-model="form.donor_name" id="donor_name" type="text" class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500/60 focus:border-green-500 shadow-sm" placeholder="Your name" />
          </div>

          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message / Intention (Optional)</label>
            <textarea v-model="form.message" id="message" rows="3" class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500/60 focus:border-green-500 shadow-sm" placeholder="Dua or purpose of donation..."></textarea>
          </div>

          <button :disabled="loading" type="submit" class="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-3 transition-colors disabled:opacity-50">
            <svg v-if="loading" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
            <span>{{ loading ? 'Processing...' : 'Donate Securely' }}</span>
          </button>

          <p class="text-[11px] text-gray-500 text-center">Secured via Paystack • We never store your card details.</p>
        </form>
      </div>
    </div>
  </div>
</template>
