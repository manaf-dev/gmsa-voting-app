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
  const availableUsers = ref<any[]>([]) // ✅ store users for candidate selection

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

      return response.data
    } catch (err: any) {
      error.value = 'Failed to create position'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Update Position and auto-refresh positions
  async function updatePosition(positionId: string, PositionDetails: object) {
    loading.value = true
    try {
      // Update position
      const response = await apiInstance.put(
        `/elections/positions/${positionId}/`,
        PositionDetails,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      // ✅ Immediately fetch updated positions
      const electionId = specificElection.value?.id
      if (electionId) {
        await fetchPositions(electionId)
      }

      return response.data
    } catch (err: any) {
      error.value = 'Failed to update position'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Delete Position and auto-refresh positions
  async function deletePosition(positionId: string) {
    loading.value = true
    try {
      await apiInstance.delete(
        `/elections/positions/${positionId}/`,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      return true
    } catch (err: any) {
      error.value = 'Failed to delete position'
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
  async function fetchPositions(electionId: string) {
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

  async function retrievePosition(positionId: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/positions/${positionId}/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      return response.data
    } catch (err: any) {
      error.value = 'Failed to retrieve election positions'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Create Candidate
  async function createCandidate(positionId: string, candidateDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.post(
        `/elections/positions/${positionId}/candidates/`,
        candidateDetails,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      // ✅ Refresh positions to update candidates
      const electionId = specificElection.value?.id
      if (electionId) {
        await retrievePosition(electionId)
      }

      return response.data
    } catch (err: any) {
      error.value = 'Failed to create candidate'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCandidates(positionId: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/positions/${positionId}/candidates/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      return response.data
    } catch (err: any) {
      error.value = 'Failed to fetch candidates'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function retrieveCandidate(candidateId: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/candidates/${candidateId}/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
      })

      return response.data
    } catch (err: any) {
      error.value = 'Failed to retrieve candidate'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Update Candidate
  async function updateCandidate(candidateId: string, candidateDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.put(
        `/elections/candidates/${candidateId}/`,
        candidateDetails,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      // ✅ Refresh positions to update candidates
      const electionId = specificElection.value?.id
      if (electionId) {
        await retrievePosition(electionId)
      }

      return response.data
    } catch (err: any) {
      error.value = 'Failed to update candidate'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Delete Candidate
  async function deleteCandidate(positionId: string, candidateId: string) {
    loading.value = true
    try {
      await apiInstance.delete(
        `/elections/positions/${positionId}/candidates/${candidateId}/`,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      // ✅ Refresh positions to update candidates
      const electionId = specificElection.value?.id
      if (electionId) {
        await retrievePosition(electionId)
      }

      return true
    } catch (err: any) {
      error.value = 'Failed to delete candidate'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ✅ Fetch all users for candidate selection
  async function fetchUsers(search?: string) {
    loading.value = true
    try {
      const params = search ? { search } : {}
      const response = await apiInstance.get('/accounts/users/', {
        headers: {
          Authorization: `Token ${localStorage.getItem('auth_token')}`,
        },
        params
      })

      availableUsers.value = response.data.results || response.data || []
      return availableUsers.value
    } catch (err: any) {
      console.error('Error fetching users:', err.response?.data || err.message)
      error.value = 'Failed to fetch users'
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

      return response.data
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
    availableUsers,
    createElection,
    createPosition,       // ✅ auto refreshes positions
    updatePosition,       // ✅ auto refreshes positions
    deletePosition,       // ✅ auto refreshes positions
    createCandidate,      // ✅ auto refreshes positions
    fetchCandidates,      // ✅ for candidate selection
    retrieveCandidate,    // ✅ for candidate selection
    updateCandidate,      // ✅ auto refreshes positions  
    deleteCandidate,      // ✅ auto refreshes positions
    retrieveElections,
    retrievePosition,
    fetchPositions,       // ✅ for election positions
    fetchElectionDetails,
    fetchUsers,           // ✅ for candidate selection
  }
})
