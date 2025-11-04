import { create } from 'zustand'
import type { Internship } from '@/types/api'
import { internshipsApi, type InternshipFilters } from '@/services/api/internships'
import { parseApiError } from '@/lib/api/error'

interface InternshipState {
  internships: Internship[]
  currentInternship: Internship | null
  loading: boolean
  error: string | null
  filters: InternshipFilters
  totalCount: number
  currentPage: number

  // Actions
  fetchInternships: () => Promise<void>
  fetchInternship: (id: number) => Promise<void>
  setFilters: (filters: Partial<InternshipFilters>) => void
  resetFilters: () => void
  setPage: (page: number) => void
}

const defaultFilters: InternshipFilters = {
  country: '',
  type: '',
  field: '',
  remote: undefined,
  search: '',
  page: 1,
  page_size: 10,
}

export const useInternshipStore = create<InternshipState>((set, get) => ({
  internships: [],
  currentInternship: null,
  loading: false,
  error: null,
  filters: defaultFilters,
  totalCount: 0,
  currentPage: 1,

  fetchInternships: async () => {
    set({ loading: true, error: null })
    try {
      const response = await internshipsApi.getInternships(get().filters)
      set({
        internships: response.data || [],
        totalCount: response.paging?.count || 0,
        loading: false,
      })
    } catch (err) {
      set({
        error: parseApiError(err),
        loading: false,
        internships: [],
      })
    }
  },

  fetchInternship: async (id: number) => {
    set({ loading: true, error: null })
    try {
      const internship = await internshipsApi.getInternship(id)
      set({
        currentInternship: internship,
        loading: false,
      })
    } catch (err) {
      set({
        error: parseApiError(err),
        loading: false,
        currentInternship: null,
      })
    }
  },

  setFilters: (newFilters: Partial<InternshipFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters, page: 1 },
      currentPage: 1,
    }))
    get().fetchInternships()
  },

  resetFilters: () => {
    set({ filters: defaultFilters, currentPage: 1 })
    get().fetchInternships()
  },

  setPage: (page: number) => {
    set((state) => ({
      filters: { ...state.filters, page },
      currentPage: page,
    }))
    get().fetchInternships()
  },
}))
