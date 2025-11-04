import { apiClient } from '@/lib/api/client'
import type { University } from '@/types/auth'
import type { ApiResponse } from '@/types/api'

const normalise = (payload: unknown): University[] => {
  if (!payload) {
    return []
  }

  if (Array.isArray(payload)) {
    return payload.map((item) => ({
      id: Number((item as { id: number }).id),
      name: String((item as { name: string }).name),
    }))
  }

  if (
    typeof payload === 'object' &&
    payload !== null &&
    'results' in payload &&
    Array.isArray((payload as { results: unknown[] }).results)
  ) {
    return normalise((payload as { results: unknown[] }).results)
  }

  if (
    typeof payload === 'object' &&
    payload !== null &&
    'data' in payload
  ) {
    const data = (payload as ApiResponse<unknown>).data
    return normalise(data)
  }

  return []
}

/**
 * Retrieve a normalised list of universities from backend.
 */
export const universitiesApi = {
  list: async (): Promise<University[]> => {
    const response = await apiClient.get<unknown>('/universities/')
    return normalise(response)
  },
}


