import api from './api'

export interface PaymentInitiation {
  payment_type: 'dues' | 'donation'
  amount: number
  currency?: string
  metadata?: any
  donor_name?: string
  message?: string
  is_anonymous?: boolean
}

export interface PaymentResponse {
  payment_id: string
  reference: string
  authorization_url: string
  access_code: string
  amount: number
  currency: string
}

export const paymentService = {
  async initiatePayment(data: PaymentInitiation): Promise<PaymentResponse> {
    const response = await api.post('/payments/initiate/', data)
    return response.data
  },

  async verifyPayment(reference: string) {
    const response = await api.get(`/payments/verify/${reference}/`)
    return response.data
  },

  async getUserPayments() {
    const response = await api.get('/payments/my-payments/')
    return response.data
  },

  async getPaymentStats() {
    const response = await api.get('/payments/stats/')
    return response.data
  },

  openPaystackCheckout(authorizationUrl: string) {
    window.open(authorizationUrl, '_blank', 'width=600,height=700')
  }
}