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
}

const defaultFilters: ExchangeProgramFilters = {
  country: '',
  university: '',
  deadline_before: '',
  search: '',
  page: 1,
  page_size: 10,
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
    set({ loading: true, error: null })
    try {
      const response = await exchangeApi.getPrograms(get().filters)
      set({
        programs: response.data || [],
        totalCount: response.paging?.count || 0,
        loading: false,
      })
    } catch (err) {
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
}))
