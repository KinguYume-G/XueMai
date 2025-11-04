import { apiClient, REFRESH_HEADER } from '@/lib/api/client'
import { setTokens } from '@/lib/auth/token'
import { parseApiError } from '@/lib/api/error'
import type { LoginPayload, RegisterPayload, TokenPair, User } from '@/types/auth'
type AuthSuccess = TokenPair & { user: User }

/**
 * Authentication related API helpers.
 */
export const authApi = {
  /**
   * Authenticate a user via credentials.
   * @param payload - login form data
   * @returns authenticated user with token pair
   */
  login: async (payload: LoginPayload): Promise<AuthSuccess> => {
    const credentials = (await apiClient.post<TokenPair>('/auth/login/', payload)) as unknown as TokenPair

    // 临时设置token以便后续请求能通过interceptor
    setTokens(credentials.access, credentials.refresh)

    const profile = (await apiClient.get<User>('/auth/me/')) as unknown as User

    return {
      access: credentials.access,
      refresh: credentials.refresh,
      user: profile,
    }
  },

  /**
   * Register a new user account (two-step process).
   * Step 1: Create account with username/email/password/password_confirm
   * Step 2: Update profile with university if provided
   * @param payload - registration data
   * @returns created user with issued tokens
   */
  register: async (payload: RegisterPayload): Promise<AuthSuccess> => {
    const { university, ...accountPayload } = payload

    try {
      const registration = (await apiClient.post<AuthSuccess>(
        '/auth/register/',
        accountPayload,
      )) as unknown as AuthSuccess

      // 使用返回的 token 执行资料补充（不假设本地已有 token）
      if (university) {
        await apiClient.put(
          '/auth/me/profile/',
          { university },
          {
            headers: {
              Authorization: `Bearer ${registration.access}`,
            },
          },
        )
      }

      const profile =
        registration.user ??
        ((await apiClient.get<User>('/auth/me/', {
          headers: {
            Authorization: `Bearer ${registration.access}`,
          },
        })) as unknown as User)

      return {
        access: registration.access,
        refresh: registration.refresh,
        user: profile,
      }
    } catch (error) {
      throw new Error(parseApiError(error))
    }
  },

  /**
   * Retrieve the current authenticated user profile.
   * @returns user profile payload
   */
  me: async (): Promise<User> => {
    const data = (await apiClient.get<User>('/auth/me/')) as unknown as User
    return data
  },

  /**
   * Refresh JWT tokens using a refresh token.
   * @param refresh - refresh token string
   * @returns refreshed token pair
   */
  refreshToken: async (refresh: string): Promise<TokenPair> => {
    const data = (await apiClient.post<TokenPair>(
      '/auth/token/refresh/',
      { refresh },
      {
        headers: {
          [REFRESH_HEADER]: 'true',
        },
      },
    )) as unknown as TokenPair
    return data
  },
}


