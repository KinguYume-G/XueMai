import { apiClient } from '@/lib/api/client';
import type { PaginatedResponse, ExchangeProgram, Internship } from '@/types/api';

export interface Startup {
  id: number;
  title: string;
  org_name: string;
  description: string;
  description_short?: string;
  city?: string;
  country?: string;
  tags: string[];
  equity_min: number | null;
  equity_max: number | null;
  contact_url?: string;
  followers_count: number;
  posted_days: number;
  created_at: string;
  updated_at: string;
}

export const opportunitiesApi = {
  /**
   * 获取交换项目列表
   */
  getExchangePrograms: async (params?: {
    page?: number;
    host_university?: number;
    search?: string;
  }): Promise<PaginatedResponse<ExchangeProgram>> => {
    const response = await apiClient.get<PaginatedResponse<ExchangeProgram>>(
      '/exchange_programs/',
      { params }
    );
    return response as PaginatedResponse<ExchangeProgram>;
  },

  /**
   * 获取单个交换项目
   */
  getExchangeProgram: async (id: number): Promise<ExchangeProgram> => {
    const response = await apiClient.get<ExchangeProgram>(`/exchange_programs/${id}/`);
    return response as ExchangeProgram;
  },

  /**
   * 获取实习机会列表
   */
  getInternships: async (params?: {
    page?: number;
    type?: string;
    company?: string;
    search?: string;
  }): Promise<PaginatedResponse<Internship>> => {
    const response = await apiClient.get<PaginatedResponse<Internship>>(
      '/internships/',
      { params }
    );
    return response as PaginatedResponse<Internship>;
  },

  /**
   * 获取单个实习机会
   */
  getInternship: async (id: number): Promise<Internship> => {
    const response = await apiClient.get<Internship>(`/internships/${id}/`);
    return response as Internship;
  },

  toggleInternshipBookmark: async (id: number): Promise<{ bookmarked: boolean }> => {
    return await apiClient.post<{ bookmarked: boolean }>(`/internships/${id}/bookmark/`) as unknown as { bookmarked: boolean };
  },

  getStartups: async (params?: {
    page?: number;
    city?: string;
    country?: string;
    search?: string;
  }): Promise<PaginatedResponse<Startup>> => {
    return await apiClient.get<PaginatedResponse<Startup>>('/startups/', { params }) as unknown as PaginatedResponse<Startup>;
  },

  createInternship: async (data: {
    title: string;
    company: string;
    description: string;
    location: string;
    type: 'full_time' | 'part_time' | 'internship' | 'remote';
    duration?: string;
    deadline?: string;
    requirements?: string;
    salary_range?: string;
    link?: string;
    skills?: string[];
    remote?: boolean;
    visibility?: 'public' | 'university' | 'private';
    is_published?: boolean;
  }): Promise<Internship> => {
    return await apiClient.post<Internship>('/internships/', data) as unknown as Internship;
  },
};
