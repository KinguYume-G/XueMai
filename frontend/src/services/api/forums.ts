import { apiClient } from '@/lib/api/client';
import type { PaginatedResponse } from '@/types/api';

export interface Forum {
  id: number;
  name: string;
  description: string;
  icon?: string;
  topics_count: number;
  created_at: string;
}

export interface Topic {
  id: number;
  forum: number;
  forum_name?: string;
  author: number;
  author_name?: string;
  title: string;
  content: string;
  tags?: string[];
  is_pinned: boolean;
  is_solved: boolean;
  views_count: number;
  replies_count: number;
  created_at: string;
  updated_at: string;
}

export interface Faculty {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon_url?: string;
  major_count: number;
  topic_count: number;
  hot_tags: string[];
}

export interface ForumOverview {
  faculty_count: number;
  major_count: number;
  active_posts: number;
  active_users: number;
}

export const forumsApi = {
  getOverview: () => apiClient.get<ForumOverview>('/forums/overview/') as unknown as Promise<ForumOverview>,
  getFaculties: async (): Promise<Faculty[]> => {
    const response = await apiClient.get<Faculty[] | PaginatedResponse<Faculty>>('/faculties/') as unknown as Faculty[] | PaginatedResponse<Faculty>;
    return Array.isArray(response) ? response : response.data;
  },
  getHotTopics: (limit = 4) => apiClient.get<Array<{ name: string; post_count: number }>>('/topics/hot/', { params: { limit } }) as unknown as Promise<Array<{ name: string; post_count: number }>>,
  /**
   * 获取论坛列表
   */
  getForums: async (): Promise<Forum[]> => {
    const response = await apiClient.get<Forum[] | PaginatedResponse<Forum>>('/forums/') as unknown as Forum[] | PaginatedResponse<Forum>;
    return Array.isArray(response) ? response : response.data;
  },

  /**
   * 获取话题列表
   */
  getTopics: async (params?: {
    page?: number;
    forum?: number;
    search?: string;
  }): Promise<PaginatedResponse<Topic>> => {
    const response = await apiClient.get<PaginatedResponse<Topic>>('/topics/', { params });
    return response as PaginatedResponse<Topic>;
  },

  /**
   * 获取单个话题
   */
  getTopic: async (id: number): Promise<Topic> => {
    return await apiClient.get<Topic>(`/topics/${id}/`) as unknown as Topic;
  },

  createTopic: async (data: {
    forum: number;
    title: string;
    content: string;
    tag_names?: string[];
  }): Promise<Topic> => {
    return await apiClient.post<Topic>('/topics/', data) as unknown as Topic;
  },
};
