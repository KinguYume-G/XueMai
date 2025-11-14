import type { Notification } from '@/types/notification'

interface NotificationItemProps {
  notification: Notification
  onClick: () => void
}

/**
 * 单条通知项组件
 * 显示通知的头像、内容、时间、未读状态
 */
export default function NotificationItem({ notification, onClick }: NotificationItemProps) {
  const { sender, message, time_ago, is_read } = notification

  // 获取用户头像或首字母
  const avatarContent = sender?.avatar ? (
    <img src={sender.avatar} alt={sender.username} className="w-full h-full object-cover" />
  ) : (
    <div className="w-full h-full flex items-center justify-center bg-blue-500 text-white text-lg font-bold">
      {sender?.username?.charAt(0).toUpperCase() || '系'}
    </div>
  )

  return (
    <div
      className={`
        flex items-start gap-4 px-6 py-4 cursor-pointer transition-colors
        ${is_read ? 'bg-white hover:bg-gray-50' : 'bg-blue-50 hover:bg-blue-100'}
      `}
      onClick={onClick}
    >
      {/* 用户头像 */}
      <div className="flex-shrink-0 w-12 h-12 rounded-full overflow-hidden">
        {avatarContent}
      </div>

      {/* 通知内容 */}
      <div className="flex-1 min-w-0">
        {/* 通知标题 */}
        <p className="text-sm font-semibold text-gray-900 mb-1">
          {notification.title}
        </p>

        {/* 通知详细信息 */}
        <p className="text-sm text-gray-600 line-clamp-2">
          {message || notification.content}
        </p>
      </div>

      {/* 时间和未读状态 */}
      <div className="flex-shrink-0 flex flex-col items-end gap-2">
        <span className="text-xs text-gray-400">
          {time_ago}
        </span>

        {/* 未读蓝点 */}
        {!is_read && (
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
        )}
      </div>
    </div>
  )
}
