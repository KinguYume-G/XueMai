import { apiClient } from '@/lib/api/client'
import type { ExchangeProgram, PaginatedResponse } from '@/types/api'

export interface ExchangeProgramFilters {
  country?: string
  university?: string
  deadline_before?: string
  search?: string
  page?: number
  limit?: number
}

export const exchangeApi = {
  /**
   * 获取交换项目列表
   */
  async getPrograms(filters: ExchangeProgramFilters = {}): Promise<PaginatedResponse<ExchangeProgram>> {
    console.log('📡 exchangeApi.getPrograms 被调用')
    console.log('📊 筛选参数:', filters)

    const params = new URLSearchParams()

    if (filters.country) params.append('country', filters.country)
    if (filters.university) params.append('university', filters.university)
    if (filters.deadline_before) params.append('deadline_before', filters.deadline_before)
    if (filters.search) params.append('search', filters.search)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())

    const queryString = params.toString()
    const url = `/exchange_programs/${queryString ? `?${queryString}` : ''}`

    console.log('🌐 请求 URL:', url)
    const response = await apiClient.get<PaginatedResponse<ExchangeProgram>>(url)
    console.log('✅ 收到响应:', response)

    return response
  },

  /**
   * 获取单个交换项目详情
   */
  async getProgram(id: number): Promise<ExchangeProgram> {
    return apiClient.get(`/exchange_programs/${id}/`)
  },

  /**
   * 获取即将截止的交换项目
   * 使用后端的 /exchange_programs/upcoming/ 接口
   */
  async getUpcoming(limit: number = 2): Promise<ExchangeProgram[]> {
    const url = `/exchange_programs/upcoming/?limit=${limit}`
    return apiClient.get(url)
  },

  /**
   * 收藏/取消收藏交换项目
   */
  async toggleBookmark(id: number): Promise<{ bookmarked: boolean }> {
    return apiClient.post(`/exchange_programs/${id}/bookmark/`)
  },
}
