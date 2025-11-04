const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const extractFromObject = (data: Record<string, unknown>): string | null => {
  // 1. 标准 detail 字段（DRF 默认格式）
  if (typeof data.detail === 'string') {
    return data.detail
  }

  // 2. 自定义错误格式：{ error: { code: "...", message: "..." | {...} } }
  if (isRecord(data.error)) {
    const errorObj = data.error
    
    // 2a. message 是字符串
    if (typeof errorObj.message === 'string') {
      return errorObj.message
    }
    
    // 2b. message 是对象（字段验证错误）
    if (isRecord(errorObj.message)) {
      const messages: string[] = []
      for (const [field, value] of Object.entries(errorObj.message)) {
        if (Array.isArray(value) && value.length > 0) {
          messages.push(`${field}: ${String(value[0])}`)
        } else if (typeof value === 'string') {
          messages.push(`${field}: ${value}`)
        }
      }
      if (messages.length > 0) {
        return messages.join('; ')
      }
    }
  }

  // 3. non_field_errors（DRF 通用错误）
  if (Array.isArray(data.non_field_errors) && data.non_field_errors[0]) {
    return String(data.non_field_errors[0])
  }

  // 4. errors 对象
  if (isRecord(data.errors)) {
    const entries = Object.values(data.errors)
    if (entries.length > 0) {
      const first = entries[0]
      if (Array.isArray(first) && first[0]) {
        return String(first[0])
      }
    }
  }

  // 5. 字段级错误（兜底逻辑）
  const fieldMessages = Object.values(data).find((value) => Array.isArray(value) && value[0])
  if (fieldMessages && Array.isArray(fieldMessages)) {
    return String(fieldMessages[0])
  }

  return null
}

/**
 * Parse API error responses into a human readable string.
 * @param error - unknown error thrown by axios/fetch
 * @returns message suitable for end-user display
 */
export const parseApiError = (error: unknown): string => {
  if (!error) {
    return '发生未知错误，请稍后重试'
  }

  if (typeof error === 'string') {
    return error
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  if (isRecord(error)) {
    if (isRecord(error.response)) {
      const response = error.response as { data?: unknown }
      if (response.data && isRecord(response.data)) {
        const extracted = extractFromObject(response.data)
        if (extracted) {
          return extracted
        }
      }
    }

    const extracted = extractFromObject(error)
    if (extracted) {
      return extracted
    }
  }

  return '请求失败，请稍后重试'
}


