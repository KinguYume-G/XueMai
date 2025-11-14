/**
 * Notification Types
 * 通知系统类型定义
 */

export type NotificationType = 'like' | 'comment' | 'follow' | 'system'

export interface NotificationSender {
  id: number
  username: string
  full_name: string
  avatar: string | null
}

export interface RelatedPost {
  id: number
  title: string
}

export interface RelatedComment {
  id: number
  content: string
}

export interface Notification {
  id: number
  notification_type: NotificationType
  type: NotificationType  // 兼容性
  title: string
  content: string
  message: string  // 格式化的消息文本
  sender: NotificationSender | null
  related_post: RelatedPost | null
  related_comment: RelatedComment | null
  link: string
  is_read: boolean
  created_at: string
  read_at: string | null
  time_ago: string  // 相对时间，如 "5分钟前"
}

export interface NotificationCountsByType {
  like: number
  comment: number
  follow: number
  system: number
}

export interface UnreadCountResponse {
  total: number
  by_type: NotificationCountsByType
  unread_count: number  // 兼容性
}

export interface NotificationListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Notification[]
  unread_count: number
  counts_by_type: NotificationCountsByType
}

export interface MarkReadResponse {
  marked_count: number
}
