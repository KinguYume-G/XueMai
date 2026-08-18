import { apiClient } from '@/lib/api/client';
import type { PaginatedResponse, ExchangeProgram, Internship, Startup } from '@/types/api';

export interface InternshipCreateRequest {
  title: string;
  company: string;
  description: string;
  location: string;
  type: Internship['type'];
  duration?: string;
  deadline?: string;
  requirements?: string;
  salary_range?: string;
  link?: string;
  city?: string;
  country?: string;
  remote?: boolean;
  skills?: string[];
  salary_min?: number;
  salary_max?: number;
  visibility?: 'public' | 'university' | 'private';
  is_published?: boolean;
}

export interface StartupCreateRequest {
  title: string;
  org_name: string;
  description: string;
  description_short?: string;
  city: string;
  country?: string;
  tags?: string[];
  equity_min?: number;
  equity_max?: number;
  contact_url?: string;
  visibility?: 'public' | 'university' | 'private';
  is_published?: boolean;
}

export const opportunitiesApi = {
  /**
   * 获取交换项目列表
   */
  getExchangePrograms: async (params?: {
    page?: number;
    limit?: number;
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
    limit?: number;
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

  createInternship: (data: InternshipCreateRequest): Promise<Internship> =>
    apiClient.post('/internships/', data),

  getStartups: (params?: {
    page?: number;
    limit?: number;
    city?: string;
    country?: string;
    tag?: string;
    search?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<Startup>> =>
    apiClient.get('/startups/', { params }),

  getStartup: (id: number): Promise<Startup> =>
    apiClient.get(`/startups/${id}/`),

  createStartup: (data: StartupCreateRequest): Promise<Startup> =>
    apiClient.post('/startups/', data),
};
