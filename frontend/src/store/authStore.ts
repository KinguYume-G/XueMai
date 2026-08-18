import { create } from 'zustand'
import { authApi } from '@/services/api/auth.api'
import type { User } from '@/types/api'
import type { LoginPayload, RegisterPayload } from '@/types/auth'
import { clearTokens, getAccessToken, setTokens } from '@/lib/auth/token'
import { parseApiError } from '@/lib/api/error'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isReady: boolean
  loading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<User>
  fetchMe: () => Promise<void>
  logout: () => void
}

/**
 * Global authentication store powered by Zustand.
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isReady: false,
  loading: false,

  login: async (payload: LoginPayload) => {
    set({ loading: true })
    try {
      const { email, password } = payload
      const { user, access, refresh } = await authApi.login({ email, password })
      setTokens(access, refresh)
      set({ user, isAuthenticated: true, isReady: true, loading: false })
    } catch (error) {
      clearTokens()
      set({ user: null, isAuthenticated: false, isReady: true, loading: false })
      throw new Error(parseApiError(error))
    }
  },

  register: async (payload: RegisterPayload) => {
    set({ loading: true })
    try {
      const { user, access, refresh } = await authApi.register(payload)
      setTokens(access, refresh)
      set({ user, isAuthenticated: true, isReady: true, loading: false })
      return user
    } catch (error) {
      clearTokens()
      set({ user: null, isAuthenticated: false, isReady: true, loading: false })
      throw new Error(parseApiError(error))
    }
  },

  fetchMe: async () => {
    const accessToken = getAccessToken()
    if (!accessToken) {
      set({ user: null, isAuthenticated: false, isReady: true, loading: false })
      return
    }

    set({ loading: true })
    try {
      const profile = await authApi.me()
      set({ user: profile, isAuthenticated: true, isReady: true, loading: false })
    } catch (error) {
      clearTokens()
      set({ user: null, isAuthenticated: false, isReady: true, loading: false })
    }
  },

  logout: () => {
    clearTokens()
    set({ user: null, isAuthenticated: false, isReady: true, loading: false })
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  },
}))

