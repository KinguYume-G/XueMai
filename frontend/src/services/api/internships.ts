import { apiClient } from '@/lib/api/client'
import type { Internship, PaginatedResponse } from '@/types/api'

export interface InternshipFilters {
  country?: string
  type?: string
  field?: string
  remote?: boolean
  search?: string
  page?: number
  page_size?: number
}

export const internshipsApi = {
  /**
   * 获取实习列表
   */
  async getInternships(filters: InternshipFilters = {}): Promise<PaginatedResponse<Internship>> {
    const params = new URLSearchParams()

    if (filters.country) params.append('country', filters.country)
    if (filters.type) params.append('type', filters.type)
    if (filters.field) params.append('field', filters.field)
    if (filters.remote !== undefined) params.append('remote', filters.remote.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())

    const queryString = params.toString()
    const url = `/internships/${queryString ? `?${queryString}` : ''}`

    return apiClient.get(url)
  },

  /**
   * 获取单个实习详情
   */
  async getInternship(id: number): Promise<Internship> {
    return apiClient.get(`/internships/${id}/`)
  },
}
