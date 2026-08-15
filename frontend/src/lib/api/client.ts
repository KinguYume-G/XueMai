import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '@/lib/auth/token'
import type { ApiError, ApiResponse } from '@/types/api'
import type { TokenPair } from '@/types/auth'

export const REFRESH_HEADER = 'X-Skip-Auth-Refresh'

const resolveBaseUrl = (): string => {
  if (typeof import.meta !== 'undefined') {
    const env = (import.meta as unknown as { env?: Record<string, string | undefined> }).env ?? {}
    if (env.VITE_API_BASE) {
      return env.VITE_API_BASE
    }
    if (env.VITE_API_BASE_URL) {
      return env.VITE_API_BASE_URL
    }
  }
  // 默认值（仅作为 fallback，实际应从 .env.local 读取）
  return 'http://127.0.0.1:8000/api'
}

/**
 * Resolved backend API base URL, configurable via environment variables.
 */
export const API_BASE_URL = resolveBaseUrl()

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise: Promise<string | null> | null = null

const resolveResponseData = <T>(response: AxiosResponse<ApiResponse<T> | T>): T => {
  const payload = response.data

  if (payload && typeof payload === 'object' && 'data' in payload) {
    if ('paging' in payload) {
      return payload as T
    }
    const extractedData = (payload as ApiResponse<T>).data
    return extractedData
  }

  return payload as T
}

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return null
  }

  try {
    const response = await axios.post<ApiResponse<TokenPair> | TokenPair>(
      `${API_BASE_URL}/auth/token/refresh/`,
      { refresh: refreshToken },
      {
        headers: {
          [REFRESH_HEADER]: 'true',
        },
      },
    )

    const payload =
      (response.data as ApiResponse<TokenPair>)?.data ?? (response.data as TokenPair)
    if (!payload?.access) {
      return null
    }

    setTokens(payload.access, payload.refresh ?? refreshToken)
    return payload.access
  } catch (error) {
    return null
  }
}

apiClient.interceptors.request.use((config) => {
  const mutableConfig = config
  const token = getAccessToken()

  if (token && mutableConfig.headers?.[REFRESH_HEADER] !== 'true') {
    mutableConfig.headers = mutableConfig.headers ?? {}
    mutableConfig.headers.Authorization = `Bearer ${token}`
  }

  return mutableConfig
})

apiClient.interceptors.response.use(
  (response) => resolveResponseData(response),
  async (error: AxiosError<ApiResponse<ApiError>>) => {
    const { response, config } = error
    const originalRequest = config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined

    if (
      response?.status === 401 &&
      originalRequest &&
      originalRequest.headers?.[REFRESH_HEADER] !== 'true' &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      }

      const newAccessToken = await refreshPromise

      if (newAccessToken) {
        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return apiClient(originalRequest)
      }

      clearTokens()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    const apiError = response?.data?.error
    if (apiError) {
      return Promise.reject(new Error(apiError.message))
    }

    return Promise.reject(error)
  },
)

/**
 * Shared Axios client configured with authentication interceptors.
 */
export { apiClient }

export default apiClient
