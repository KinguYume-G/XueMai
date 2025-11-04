import { apiClient } from '@/lib/api/client';
import type { PaginatedResponse } from '@/types/api';

export interface UniversityResource {
  id: number;
  university: number;
  university_name?: string;
  category: 'course' | 'canteen' | 'club' | 'event' | 'notice';
  category_display?: string;
  title: string;
  content: string;
  extra?: Record<string, unknown>;
  is_active: boolean;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export const campusApi = {
  /**
   * 获取大学资源列表（APU 专区等）
   */
  getUniversityResources: async (
    universitySlug: string,
    params?: {
      category?: string;
      page?: number;
    }
  ): Promise<PaginatedResponse<UniversityResource>> => {
    const response = await apiClient.get<PaginatedResponse<UniversityResource>>(
      `/universities/${universitySlug}/resources/`,
      { params }
    );
    return response as PaginatedResponse<UniversityResource>;
  },
};

