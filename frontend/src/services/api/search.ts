import { apiClient } from '@/lib/api/client'

export interface SearchUserResult {
  id: number
  username: string
  avatar_url?: string
  major?: string
  university?: string
}

export interface SearchContentResult {
  id: number
  title: string
  excerpt?: string
  author?: string
  forum_id?: number
  created_at?: string
}

export interface SearchCommunityResult {
  id: number
  slug: string
  name: string
  description: string
  members: number
}

export interface SearchOpportunityResult {
  id: number
  kind: 'exchange' | 'internship' | 'startup'
  title: string
  subtitle: string
}

export interface GlobalSearchResponse {
  query: string
  total: number
  results: {
    users?: SearchUserResult[]
    posts?: SearchContentResult[]
    topics?: SearchContentResult[]
    communities?: SearchCommunityResult[]
    opportunities?: SearchOpportunityResult[]
  }
}

export const searchApi = {
  search: (query: string, type = 'all', limit = 12) =>
    apiClient.get<GlobalSearchResponse>('/search/', {
      params: { q: query, type, limit },
    }),
}
