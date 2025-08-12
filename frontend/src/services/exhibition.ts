import api from './api'

export interface ExhibitionLookupResponse { status: 'found' | 'not_found'; message: string }
export interface ExhibitionRegisterPayload {
  phone: string
  first_name: string
  last_name: string
  student_id?: string
  program?: string
  year_of_study?: string
}

export async function exhibitionLookup(phone: string) {
  const res = await api.post<ExhibitionLookupResponse>('/accounts/exhibition/lookup/', { phone })
  return res.data
}

export async function exhibitionRegister(payload: ExhibitionRegisterPayload) {
  const res = await api.post('/accounts/exhibition/register/', payload)
  return res.data as { status: string; message: string }
}
