// src/stores/electionStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiInstance from '@/services/api'

export const useElectionStore = defineStore('election', () => {
  const router = useRouter()

  const loading = ref(false)
  const error = ref<string | null>(null)

  const availableElections = ref<any[]>([]) 
  const specificElection = ref<any | null>(null)
  const electionPositions = ref<any[]>([]) // ✅ store positions separately

  // Create Election
  async function createElection(ElectionDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.post('/elections/', ElectionDetails, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })
      return response.data
    } catch (err: any) {
      error.value = 'Failed to create election'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Create Position and auto-refresh positions
  async function createPosition(electionId: string, PositionDetails: object) {
    loading.value = true
    try {
      // Create position
      const response = await apiInstance.post(
        `/elections/${electionId}/positions/`,
        PositionDetails,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      // ✅ Immediately fetch updated positions
      await retrievePositions(electionId)

      return response.data
    } catch (err: any) {
      error.value = 'Failed to create position'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Retrieve all elections
  async function retrieveElections() {
    loading.value = true
    try {
      const response = await apiInstance.get('/elections/', {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      availableElections.value = response.data.results || []
      return availableElections.value
    } catch (err: any) {
      error.value = 'Failed to retrieve elections'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Retrieve positions for a specific election
  async function retrievePositions(electionId: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/${electionId}/positions/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      electionPositions.value = response.data.results || []
      return electionPositions.value
    } catch (err: any) {
      error.value = 'Failed to retrieve election positions'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch single election
  async function fetchElectionDetails(id: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/${id}/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      specificElection.value = response.data
      return specificElection.value
    } catch (err: any) {
      error.value = 'Failed to retrieve election details'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    availableElections,
    specificElection,
    electionPositions,
    createElection,
    createPosition,       // ✅ auto refreshes positions
    retrieveElections,
    retrievePositions,
    fetchElectionDetails,
  }
})
