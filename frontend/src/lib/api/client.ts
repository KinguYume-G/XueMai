import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '@/lib/auth/token'
import {
  buildApiUrl,
  DEFAULT_API_BASE_URL,
  extractApiErrorMessage,
  resolveApiPayload,
} from '@/lib/api/contracts'
import type { ApiError, ApiResponse } from '@/types/api'
import type { TokenPair } from '@/types/auth'

export const REFRESH_HEADER = 'X-Skip-Auth-Refresh'

/**
 * The response interceptor removes Axios' transport wrapper. This interface
 * keeps the public client type aligned with that runtime behaviour.
 */
export interface ApiClient {
  request<T = unknown, D = unknown>(config: AxiosRequestConfig<D>): Promise<T>
  get<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  delete<T = unknown, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<T>
  post<T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig<D>,
  ): Promise<T>
  put<T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig<D>,
  ): Promise<T>
  patch<T = unknown, D = unknown>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig<D>,
  ): Promise<T>
}

/**
 * Browser requests always use the same-origin API path. During development,
 * Vite proxies this path to Django; production can route it at the web server.
 */
export const API_BASE_URL = DEFAULT_API_BASE_URL

const axiosClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise: Promise<string | null> | null = null

const resolveResponseData = <T>(
  response: AxiosResponse<ApiResponse<T> | T>,
): ApiResponse<T> | T => {
  return resolveApiPayload(response.data) as ApiResponse<T> | T
}

export const apiFetch = (path: string, init: RequestInit = {}): Promise<Response> => {
  const headers = new Headers(init.headers)
  const token = getAccessToken()

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  return fetch(buildApiUrl(path, API_BASE_URL), {
    ...init,
    headers,
  })
}

export const readApiErrorMessage = async (
  response: Response,
  fallback = `请求失败 (${response.status})`,
): Promise<string> => {
  try {
    return extractApiErrorMessage(await response.clone().json(), fallback)
  } catch {
    try {
      const text = await response.clone().text()
      return text.trim() || fallback
    } catch {
      return fallback
    }
  }
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
  } catch {
    return null
  }
}

axiosClient.interceptors.request.use((config) => {
  const mutableConfig = config
  const token = getAccessToken()

  if (token && mutableConfig.headers?.[REFRESH_HEADER] !== 'true') {
    mutableConfig.headers = mutableConfig.headers ?? {}
    mutableConfig.headers.Authorization = `Bearer ${token}`
  }

  return mutableConfig
})

axiosClient.interceptors.response.use(
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
        return axiosClient(originalRequest)
      }

      clearTokens()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    if (response?.data) {
      return Promise.reject(
        new Error(extractApiErrorMessage(response.data, error.message)),
      )
    }

    return Promise.reject(error)
  },
)

/**
 * Shared Axios client configured with authentication interceptors.
 */
export const apiClient = axiosClient as unknown as ApiClient

export default apiClient
