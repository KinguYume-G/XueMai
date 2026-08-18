import { apiClient } from '@/lib/api/client'
import type { ApiResponse } from '@/types/api'

export interface UniversitySummary {
  id: number
  name: string
  slug: string
  country?: string
  city?: string
  students_count?: number
}

const normalise = (payload: unknown): UniversitySummary[] => {
  if (!payload) {
    return []
  }

  if (Array.isArray(payload)) {
    return payload.map((item) => ({
      id: Number((item as { id: number }).id),
      name: String((item as { name: string }).name),
      slug: String((item as { slug?: string }).slug ?? ''),
      country: (item as { country?: string }).country,
      city: (item as { city?: string }).city,
      students_count: Number((item as { students_count?: number }).students_count ?? 0),
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
  list: async (): Promise<UniversitySummary[]> => {
    const response = await apiClient.get<unknown>('/universities/')
    return normalise(response)
  },
}

