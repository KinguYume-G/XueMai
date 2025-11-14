/**
 * Time Formatting Utilities
 * 时间格式化工具函数
 */

/**
 * 将ISO时间戳转换为相对时间
 * @param isoString ISO格式时间字符串
 * @returns 相对时间字符串，如 "刚刚"、"5分钟前"、"3小时前"、"昨天"、"3天前"、"10月15日"
 */
export function formatTimeAgo(isoString: string): string {
  if (!isoString) {
    return ''
  }

  const now = new Date()
  const date = new Date(isoString)
  const diffMs = now.getTime() - date.getTime()

  // 转换为不同单位
  const seconds = Math.floor(diffMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  // 根据时间差返回不同格式
  if (seconds < 60) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    // 7天以上显示具体日期 "MM月DD日"
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}月${day}日`
  }
}

/**
 * 格式化完整日期时间
 * @param isoString ISO格式时间字符串
 * @returns 格式化的日期时间字符串，如 "2024-11-09 10:30"
 */
export function formatDateTime(isoString: string): string {
  if (!isoString) {
    return ''
  }

  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}`
}

/**
 * 格式化日期（不包含时间）
 * @param isoString ISO格式时间字符串
 * @returns 格式化的日期字符串，如 "2024-11-09"
 */
export function formatDate(isoString: string): string {
  if (!isoString) {
    return ''
  }

  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}
