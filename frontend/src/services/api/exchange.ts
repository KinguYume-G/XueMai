import { apiClient } from '@/lib/api/client'
import type { ExchangeProgram, PaginatedResponse } from '@/types/api'

export interface ExchangeProgramFilters {
  country?: string
  university?: string
  deadline_before?: string
  search?: string
  page?: number
  page_size?: number
}

export const exchangeApi = {
  /**
   * 获取交换项目列表
   */
  async getPrograms(filters: ExchangeProgramFilters = {}): Promise<PaginatedResponse<ExchangeProgram>> {
    const params = new URLSearchParams()

    if (filters.country) params.append('country', filters.country)
    if (filters.university) params.append('university', filters.university)
    if (filters.deadline_before) params.append('deadline_before', filters.deadline_before)
    if (filters.search) params.append('search', filters.search)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())

    const queryString = params.toString()
    const url = `/exchange_programs/${queryString ? `?${queryString}` : ''}`

    return apiClient.get(url)
  },

  /**
   * 获取单个交换项目详情
   */
  async getProgram(id: number): Promise<ExchangeProgram> {
    return apiClient.get(`/exchange_programs/${id}/`)
  },

  /**
   * 获取即将截止的交换项目（未来14天内）
   */
  async getUpcoming(limit: number = 2): Promise<ExchangeProgram[]> {
    const today = new Date()
    const futureDate = new Date()
    futureDate.setDate(today.getDate() + 14)

    const deadlineBefore = futureDate.toISOString().split('T')[0]

    const response = await this.getPrograms({
      deadline_before: deadlineBefore,
      page_size: limit,
    })

    // 过滤出截止日期在未来的项目
    const upcomingPrograms = (response.data || []).filter((program) => {
      if (!program.deadline) return false
      const deadline = new Date(program.deadline)
      return deadline >= today && deadline <= futureDate
    })

    return upcomingPrograms.slice(0, limit)
  },
}
