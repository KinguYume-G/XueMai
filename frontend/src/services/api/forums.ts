import { apiClient } from '@/lib/api/client'
import type { PaginatedResponse, PublicUser, Tag, Visibility } from '@/types/api'

export interface Faculty {
  id: number
  name: string
  slug: string
  icon_url?: string
  description: string
  major_count: number
  topic_count: number
  created_at: string
}

export interface Forum {
  id: number
  name: string
  description: string
  icon?: string
  topics_count: number
  created_at: string
}

export interface Topic {
  id: number
  forum: number
  forum_name: string
  author: PublicUser
  title: string
  content: string
  tags: Tag[]
  is_pinned: boolean
  is_solved: boolean
  visibility: Exclude<Visibility, 'followers'>
  is_published: boolean
  views_count: number
  replies_count: number
  created_at: string
  updated_at: string
}

export interface ForumOverview {
  faculty_count: number
  major_count: number
  active_posts: number
  active_users: number
}

export interface HotTopic {
  name: string
  post_count: number
}

export interface TopicCreateRequest {
  forum: number
  title: string
  content: string
  tag_names?: string[]
  visibility?: 'public' | 'university' | 'private'
  is_published?: boolean
}

export const forumsApi = {
  getForums: (params?: { limit?: number; search?: string }) =>
    apiClient.get<PaginatedResponse<Forum>>('/forums/', { params }),

  getFaculties: (params?: { limit?: number; search?: string }) =>
    apiClient.get<PaginatedResponse<Faculty>>('/faculties/', { params }),

  getOverview: () => apiClient.get<ForumOverview>('/forums/overview/'),

  getHotTopics: (limit = 6, window = '30d') =>
    apiClient.get<HotTopic[]>('/topics/hot/', { params: { limit, window } }),

  getTopics: (params?: {
    page?: number
    limit?: number
    forum?: number
    search?: string
    ordering?: string
  }) => apiClient.get<PaginatedResponse<Topic>>('/topics/', { params }),

  getTopic: (id: number) => apiClient.get<Topic>(`/topics/${id}/`),

  createTopic: (data: TopicCreateRequest) =>
    apiClient.post<TopicCreateRequest>('/topics/', data),
}
