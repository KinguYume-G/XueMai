import { apiClient } from '@/lib/api/client'
import type { Tag, PaginatedResponse } from '@/types/api'

export const tagsApi = {
  /**
   * 获取热门标签（按帖子数量排序）
   */
  async getHotTags(limit: number = 4): Promise<Tag[]> {
    const response: any = await apiClient.get(
      `/tags/?ordering=-posts_count&page_size=${limit}`
    )
    // Handle both array and paginated response formats
    if (Array.isArray(response)) {
      return response
    }
    return response.data || response.results || []
  },

  /**
   * 获取所有标签
   */
  async getAllTags(): Promise<Tag[]> {
    const response: any = await apiClient.get('/tags/')
    // Handle both array and paginated response formats
    if (Array.isArray(response)) {
      return response
    }
    return response.data || response.results || []
  },
}
