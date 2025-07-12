import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

interface Election {
  id: string
  title: string
  description: string
  start_date: string
  end_date: string
  status: 'upcoming' | 'active' | 'completed' | 'cancelled'
  total_votes: number
  total_voters: number
  is_active: boolean
  can_vote: boolean
  created_by_name: string
  created_at: string
  positions?: Position[]
}

interface Position {
  id: number
  title: string
  description: string
  total_votes: number
  candidates: Candidate[]
}

interface Candidate {
  id: number
  name: string
  student_id: string
  year_of_study: string
  program: string
  manifesto: string
  profile_picture?: string
  vote_count: number
  vote_percentage: number
}

interface Vote {
  position_id: number
  position_title: string
  candidate_id: number
  candidate_name: string
  timestamp: string
}

export const useElectionsStore = defineStore('elections', () => {
  const elections = ref<Election[]>([])
  const currentElection = ref<Election | null>(null)
  const userVotes = ref<Vote[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const fetchElections = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get('/elections/')
      elections.value = response.data.results || response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch elections'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchElection = async (id: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/elections/${id}/`)
      currentElection.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch election'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const castVote = async (positionId: number, candidateId: number) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/elections/${currentElection.value?.id}/vote/`, {
        position_id: positionId,
        candidate_id: candidateId
      })
      
      // Refresh user votes
      if (currentElection.value) {
        await fetchUserVotes(currentElection.value.id)
      }
      
      return response.data
    } catch (err: any) {
      if (err.response?.status === 402) {
        error.value = err.response.data.error
        return { requiresPayment: true }
      }
      error.value = err.response?.data?.error || 'Failed to cast vote'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserVotes = async (electionId: string) => {
    try {
      const response = await api.get(`/elections/${electionId}/my-votes/`)
      userVotes.value = response.data.voted_positions || []
    } catch (err: any) {
      if (err.response?.status === 402) {
        return { requiresPayment: true }
      }
      console.error('Failed to fetch user votes:', err)
    }
  }

  const fetchElectionResults = async (electionId: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/elections/${electionId}/results/`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch results'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const hasVotedForPosition = (positionId: number): boolean => {
    return userVotes.value.some(vote => vote.position_id === positionId)
  }

  const getVoteForPosition = (positionId: number): Vote | undefined => {
    return userVotes.value.find(vote => vote.position_id === positionId)
  }

  const createElection = async (electionData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post('/elections/', electionData)
      
      // Add the new election to our local state
      elections.value.unshift(response.data)
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to create election'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    elections,
    currentElection,
    userVotes,
    isLoading,
    error,
    fetchElections,
    fetchElection,
    castVote,
    fetchUserVotes,
    fetchElectionResults,
    hasVotedForPosition,
    getVoteForPosition,
    createElection
  }
})