export const DEFAULT_API_BASE_URL = '/api'

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

export const normalizeApiBaseUrl = (baseUrl = DEFAULT_API_BASE_URL): string => {
  const normalized = baseUrl.trim().replace(/\/+$/, '')
  return normalized || DEFAULT_API_BASE_URL
}

export const buildApiUrl = (
  path: string,
  baseUrl = DEFAULT_API_BASE_URL,
): string => {
  if (/^https?:\/\//i.test(path)) {
    return path
  }

  const base = normalizeApiBaseUrl(baseUrl)
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (normalizedPath === base || normalizedPath.startsWith(`${base}/`)) {
    return normalizedPath
  }

  return `${base}${normalizedPath}`
}

const collectMessages = (value: unknown, prefix?: string): string[] => {
  if (typeof value === 'string' && value.trim()) {
    return [prefix ? `${prefix}: ${value}` : value]
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => collectMessages(item, prefix))
  }

  if (!isRecord(value)) {
    return []
  }

  if (value.error !== undefined) {
    const nested = collectMessages(value.error)
    if (nested.length > 0) return nested
  }

  if (value.message !== undefined) {
    const nested = collectMessages(value.message)
    if (nested.length > 0) return nested
  }

  if (typeof value.detail === 'string' && value.detail.trim()) {
    return [value.detail]
  }

  return Object.entries(value).flatMap(([key, item]) =>
    collectMessages(item, key),
  )
}

export const extractApiErrorMessage = (
  value: unknown,
  fallback = '请求失败，请稍后重试',
): string => {
  const messages = collectMessages(value)
  return messages.length > 0 ? [...new Set(messages)].join('; ') : fallback
}

export interface ApiEnvelopeLike<T> {
  data: T
  error: unknown
  paging?: unknown
}

export const resolveApiPayload = <T>(payload: ApiEnvelopeLike<T> | T): T | ApiEnvelopeLike<T> => {
  if (isRecord(payload) && 'data' in payload && 'error' in payload) {
    const envelope = payload as unknown as ApiEnvelopeLike<T>
    return envelope.paging != null ? envelope : envelope.data
  }

  return payload as T
}

export const extractConversationId = (event: unknown): number | undefined => {
  if (!isRecord(event)) return undefined

  const rawId = event.conversation_id
  if (typeof rawId === 'number' && Number.isInteger(rawId) && rawId > 0) {
    return rawId
  }

  if (typeof rawId === 'string' && /^\d+$/.test(rawId)) {
    const parsed = Number(rawId)
    return parsed > 0 ? parsed : undefined
  }

  return undefined
}

export interface SseFrameSplit {
  frames: string[]
  remainder: string
}

export const splitSseFrames = (buffer: string, flush = false): SseFrameSplit => {
  const normalized = buffer.replace(/\r\n/g, '\n')
  const parts = normalized.split('\n\n')
  const remainder = flush ? '' : parts.pop() ?? ''

  if (flush) {
    const last = parts[parts.length - 1]
    if (last === '') parts.pop()
  }

  return {
    frames: parts.filter((part) => part.trim().length > 0),
    remainder,
  }
}

export const getSseData = (frame: string): string | null => {
  const dataLines = frame
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())

  return dataLines.length > 0 ? dataLines.join('\n').trim() : null
}
