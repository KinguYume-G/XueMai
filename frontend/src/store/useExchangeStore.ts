import { create } from 'zustand'
import type { ExchangeProgram } from '@/types/api'
import { exchangeApi, type ExchangeProgramFilters } from '@/services/api/exchange'
import { parseApiError } from '@/lib/api/error'

interface ExchangeState {
  programs: ExchangeProgram[]
  currentProgram: ExchangeProgram | null
  loading: boolean
  error: string | null
  filters: ExchangeProgramFilters
  totalCount: number
  currentPage: number

  // Actions
  fetchPrograms: () => Promise<void>
  fetchProgram: (id: number) => Promise<void>
  setFilters: (filters: Partial<ExchangeProgramFilters>) => void
  resetFilters: () => void
  setPage: (page: number) => void
  toggleBookmark: (id: number) => Promise<void>
}

const defaultFilters: ExchangeProgramFilters = {
  country: '',
  university: '',
  deadline_before: '',
  search: '',
  page: 1,
  limit: 20,
}

export const useExchangeStore = create<ExchangeState>((set, get) => ({
  programs: [],
  currentProgram: null,
  loading: false,
  error: null,
  filters: defaultFilters,
  totalCount: 0,
  currentPage: 1,

  fetchPrograms: async () => {
    console.log('🔄 fetchPrograms 被调用')
    console.log('📊 当前筛选条件:', get().filters)

    set({ loading: true, error: null })

    try {
      console.log('📡 准备调用 API: exchangeApi.getPrograms()')
      const response = await exchangeApi.getPrograms(get().filters)

      console.log('✅ API 响应 (经过拦截器处理):', response)
      console.log('📦 response 类型:', typeof response)
      console.log('📦 response 是数组?', Array.isArray(response))

      // 🔥 关键修复：apiClient 的响应拦截器会自动提取 data 字段
      // 所以 response 可能已经是数据数组，而不是 { data: [...], paging: {...} }
      let programs: ExchangeProgram[] = []
      let totalCount = 0

      if (Array.isArray(response)) {
        // 拦截器已经提取了 data 字段，response 就是数组
        programs = response
        totalCount = response.length
        console.log('✅ 数据格式：response 本身是数组 (拦截器已提取)')
      } else if (response && typeof response === 'object') {
        // 可能还是完整的响应对象
        const anyResponse = response as any

        if (Array.isArray(anyResponse.data)) {
          programs = anyResponse.data
          totalCount = anyResponse.paging?.count || anyResponse.data.length
          console.log('✅ 数据格式：response.data 是数组')
        } else if (anyResponse.results && Array.isArray(anyResponse.results)) {
          programs = anyResponse.results
          totalCount = anyResponse.count || anyResponse.results.length
          console.log('✅ 数据格式：response.results 是数组')
        } else {
          console.error('❌ 未知的响应格式:', response)
        }
      }

      console.log(`✅ 成功获取 ${programs.length} 个交换项目`)
      console.log('📋 项目列表前3个:', programs.slice(0, 3))

      set({
        programs: programs,
        totalCount: totalCount,
        loading: false,
      })
    } catch (err: any) {
      console.error('❌ fetchPrograms 错误:', err)
      console.error('错误详情:', {
        message: err.message,
        response: err.response,
        config: err.config
      })

      set({
        error: parseApiError(err),
        loading: false,
        programs: [],
      })
    }
  },

  fetchProgram: async (id: number) => {
    set({ loading: true, error: null })
    try {
      const program = await exchangeApi.getProgram(id)
      set({
        currentProgram: program,
        loading: false,
      })
    } catch (err) {
      set({
        error: parseApiError(err),
        loading: false,
        currentProgram: null,
      })
    }
  },

  setFilters: (newFilters: Partial<ExchangeProgramFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters, page: 1 },
      currentPage: 1,
    }))
    get().fetchPrograms()
  },

  resetFilters: () => {
    set({ filters: defaultFilters, currentPage: 1 })
    get().fetchPrograms()
  },

  setPage: (page: number) => {
    set((state) => ({
      filters: { ...state.filters, page },
      currentPage: page,
    }))
    get().fetchPrograms()
  },

  toggleBookmark: async (id: number) => {
    try {
      await exchangeApi.toggleBookmark(id)
      // 更新本地状态
      set((state) => ({
        programs: state.programs.map((program) =>
          program.id === id ? { ...program, bookmarked: !program.bookmarked } : program
        ),
        currentProgram:
          state.currentProgram?.id === id
            ? { ...state.currentProgram, bookmarked: !state.currentProgram.bookmarked }
            : state.currentProgram,
      }))
    } catch (err) {
      console.error('Toggle bookmark error:', err)
    }
  },
}))
