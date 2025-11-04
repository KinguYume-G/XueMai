import { apiClient } from '@/lib/api/client';
import type { PaginatedResponse, ExchangeProgram, Internship } from '@/types/api';

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
};

