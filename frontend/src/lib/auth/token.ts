/**
 * Token storage utilities for authentication.
 * All functions guard against non-browser environments to remain SSR safe.
 */

const ACCESS_TOKEN_KEY = 'xm_access_token'
const REFRESH_TOKEN_KEY = 'xm_refresh_token'

const isBrowser = (): boolean => typeof window !== 'undefined'

/**
 * Retrieve the persisted access token.
 * @returns access token string or null when unavailable
 */
export const getAccessToken = (): string | null => {
  if (!isBrowser()) {
    return null
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

/**
 * Retrieve the persisted refresh token.
 * @returns refresh token string or null when unavailable
 */
export const getRefreshToken = (): string | null => {
  if (!isBrowser()) {
    return null
  }
  return window.localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * Persist freshly issued access and refresh tokens.
 * @param access - new access token
 * @param refresh - new refresh token
 */
export const setTokens = (access: string, refresh: string): void => {
  if (!isBrowser()) {
    return
  }
  window.localStorage.setItem(ACCESS_TOKEN_KEY, access)
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

/**
 * Remove all locally stored authentication tokens.
 */
export const clearTokens = (): void => {
  if (!isBrowser()) {
    return
  }
  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  window.localStorage.removeItem(REFRESH_TOKEN_KEY)
}


