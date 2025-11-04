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

export const forumsApi = {
  /**
   * 获取论坛列表
   */
  getForums: async (): Promise<Forum[]> => {
    const response = await apiClient.get<{ data: Forum[] }>('/forums/');
    return (response as { data: Forum[] }).data;
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
    const response = await apiClient.get<{ data: Topic }>(`/topics/${id}/`);
    return (response as { data: Topic }).data;
  },
};

