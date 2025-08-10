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
  const electionPositions = ref<any[]>([]) 
  const availableUsers = ref<any[]>([]) 

  // Create Election
  async function createElection(ElectionDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.post('/elections/', ElectionDetails, )
      return response.data
    } catch (err: any) {
      error.value = 'Failed to create election'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function createPosition(electionId: string, PositionDetails: object) {
    loading.value = true
    try {
      // Create position
      const response = await apiInstance.post(
        `/elections/${electionId}/positions/`,
        PositionDetails,
        
      )

      return response.data
    } catch (err: any) {
      error.value = 'Failed to create position'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function updatePosition(positionId: string, PositionDetails: object) {
    loading.value = true
    try {
      // Update position
      const response = await apiInstance.put(
        `/elections/positions/${positionId}/`,
        PositionDetails,
        
      )

      return response.data
    } catch (err: any) {
      error.value = 'Failed to update position'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function deletePosition(positionId: string) {
    loading.value = true
    try {
      await apiInstance.delete(
        `/elections/positions/${positionId}/`,
        
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
      const response = await apiInstance.get('/elections/', )

      availableElections.value = response.data.results || []
      return availableElections.value
    } catch (err: any) {
      error.value = 'Failed to retrieve elections'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function fetchPositions(electionId: string) {
    loading.value = true
    try {
      const response = await apiInstance.get(`/elections/${electionId}/positions/`, )

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
      const response = await apiInstance.get(`/elections/positions/${positionId}/`, )

      return response.data
    } catch (err: any) {
      error.value = 'Failed to retrieve election positions'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function createCandidate(positionId: string, candidateDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.post(
        `/elections/positions/${positionId}/candidates/`,
        candidateDetails,
        
      )

      
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
      const response = await apiInstance.get(`/elections/positions/${positionId}/candidates/`, )

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
      const response = await apiInstance.get(`/elections/candidates/${candidateId}/`, )

      return response.data
    } catch (err: any) {
      error.value = 'Failed to retrieve candidate'
      throw err
    } finally {
      loading.value = false
    }
  }

  
  async function updateCandidate(candidateId: string, candidateDetails: object) {
    loading.value = true
    try {
      const response = await apiInstance.put(
        `/elections/candidates/${candidateId}/`,
        candidateDetails,
        
      )

      
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

  
  async function deleteCandidate(positionId: string, candidateId: string) {
    loading.value = true
    try {
      await apiInstance.delete(
        `/elections/positions/${positionId}/candidates/${candidateId}/`,
        
      )

      
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

 
  async function fetchUsers(search?: string) {
    loading.value = true
    try {
      const params = search ? { search } : {}
      const response = await apiInstance.get('/accounts/users/', { params })

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
      const response = await apiInstance.get(`/elections/${id}/`, )

      return response.data
    } catch (err: any) {
      error.value = 'Failed to retrieve election details'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Submit full ballot (bulk selections) in one request
  async function submitBallot(
    electionId: string,
    selections: Array<{ position_id: string; candidate_id?: string; approve?: boolean }>
  ) {
    loading.value = true
    try {
      const payload = {
        election_id: electionId,
        selections,
      }
      const response = await apiInstance.post('/elections/vote/', payload)
      return response.data
    } catch (err: any) {
      error.value = err?.response?.data?.error || 'Failed to submit ballot'
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
    createPosition,       
    updatePosition,       
    deletePosition,       
    createCandidate,      
    fetchCandidates,      
    retrieveCandidate,    
    updateCandidate,      
    deleteCandidate,      
    retrieveElections,
    retrievePosition,
    fetchPositions,       
    fetchElectionDetails,
    fetchUsers,
    submitBallot,
  }
})
