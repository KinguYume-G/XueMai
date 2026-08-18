import { apiClient } from '@/lib/api/client'
import type { PaginatedResponse } from '@/types/api'

export type CommunityCategory = 'interest' | 'city' | 'oncampus' | 'study_group'

export interface CommunityRecord {
  id: number
  name: string
  slug: string
  description: string
  cover_url?: string
  category: CommunityCategory
  city?: string
  is_oncampus: boolean
  is_study_group: boolean
  members: number
  activity_rate: number
  visibility: 'public' | 'university' | 'private'
  is_published: boolean
  joined: boolean
  created_at: string
  updated_at: string
}

export interface CommunityCreateRequest {
  name: string
  slug: string
  description?: string
  cover_url?: string
  category: CommunityCategory
  city?: string
  is_oncampus?: boolean
  is_study_group?: boolean
  visibility?: 'public' | 'university' | 'private'
  is_published?: boolean
}

export interface CommunityJoinResponse {
  joined: boolean
  message: string
}

export const communitiesApi = {
  getCommunities: (params?: {
    page?: number
    limit?: number
    search?: string
    category?: CommunityCategory
    city?: string
    ordering?: string
  }) => apiClient.get<PaginatedResponse<CommunityRecord>>('/communities/', { params }),

  getCommunity: (slug: string) =>
    apiClient.get<CommunityRecord>(`/communities/${encodeURIComponent(slug)}/`),

  createCommunity: (data: CommunityCreateRequest) =>
    apiClient.post<CommunityRecord>('/communities/', data),

  toggleJoin: (slug: string) =>
    apiClient.post<CommunityJoinResponse | undefined>(
      `/communities/${encodeURIComponent(slug)}/join/`,
    ),
}
