import { apiClient } from '@/lib/api/client'
import type { PaginatedResponse } from '@/types/api'

export type CommunityCategory = 'interest' | 'city' | 'oncampus' | 'study_group'

export interface Community {
  id: number
  name: string
  slug: string
  description: string
  cover_url?: string | null
  category: CommunityCategory
  city?: string | null
  members: number
  activity_rate: number
  joined: boolean
}

export const communitiesApi = {
  list: (params?: { category?: CommunityCategory; search?: string }) =>
    apiClient.get<PaginatedResponse<Community>>('/communities/', { params }) as unknown as Promise<PaginatedResponse<Community>>,

  create: (data: {
    name: string
    description?: string
    category: CommunityCategory
    city?: string
    cover_url?: string
    is_oncampus?: boolean
    is_study_group?: boolean
  }) => apiClient.post<Community>('/communities/', data) as unknown as Promise<Community>,

  toggleJoin: (slug: string) =>
    apiClient.post<{ joined: boolean }>(`/communities/${slug}/join/`) as unknown as Promise<{ joined: boolean }>,
}
