import { useState, useEffect, useCallback } from 'react'
import { Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { notificationsApi } from '@/services/api/notifications'
import type { Notification, NotificationType, NotificationCountsByType } from '@/types/notification'
import NotificationItem from '@/components/notifications/NotificationItem'

type TabType = 'all' | NotificationType

/**
 * 通知页面
 * 使用标准三栏布局：左侧导航 + 中间通知内容 + 右侧侧边栏
 */
export default function Notifications() {
  const [activeTab, setActiveTab] = useState<TabType>('all')
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [counts, setCounts] = useState<NotificationCountsByType>({
    like: 0,
    comment: 0,
    follow: 0,
    system: 0,
  })
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)

  // 获取通知列表
  const fetchNotifications = useCallback(async (type?: NotificationType) => {
    console.log('🔵 [NotificationsPage] fetchNotifications 开始, type:', type)
    setLoading(true)
    try {
      const data = await notificationsApi.getNotifications({
        type,
        page: 1,
      })

      console.log('🟢 [NotificationsPage] API 返回成功, data:', data)

      // 修复：优先检查 data 是否直接是数组
      const notificationsArray = Array.isArray(data) ? data : (data?.results || [])
      console.log('🟠 [NotificationsPage] notificationsArray 长度:', notificationsArray.length)

      setNotifications(notificationsArray)

      // 如果 data 是数组，需要计算统计数据；如果是对象，使用对象中的字段
      if (Array.isArray(data)) {
        // data 是数组，需要手动计算统计数据
        const unreadNotifications = notificationsArray.filter((n: Notification) => !n.is_read)
        const calculatedUnreadCount = unreadNotifications.length

        // 按类型统计所有通知数量（不是只统计未读）
        const calculatedCounts: NotificationCountsByType = {
          like: notificationsArray.filter((n: Notification) => n.type === 'like').length,
          comment: notificationsArray.filter((n: Notification) => n.type === 'comment').length,
          follow: notificationsArray.filter((n: Notification) => n.type === 'follow').length,
          system: notificationsArray.filter((n: Notification) => n.type === 'system').length,
        }

        setUnreadCount(calculatedUnreadCount)
        setCounts(calculatedCounts)
      } else {
        // data 是对象，使用对象中的字段
        setUnreadCount(data.unread_count || 0)
        if (data.counts_by_type) {
          setCounts(data.counts_by_type)
        }
      }
    } catch (error) {
      console.error('❌ [NotificationsPage] Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // 初始加载
  useEffect(() => {
    fetchNotifications()
  }, [fetchNotifications])

  // 切换标签
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    if (tab === 'all') {
      fetchNotifications()
    } else {
      fetchNotifications(tab as NotificationType)
    }
  }

  // 一键已读
  const handleMarkAllAsRead = async () => {
    try {
      const type = activeTab !== 'all' ? (activeTab as NotificationType) : undefined
      await notificationsApi.markAllAsRead(type)
      fetchNotifications(type)
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    }
  }

  // 点击单条通知
  const handleNotificationClick = async (notification: Notification) => {
    // 标记为已读
    if (!notification.is_read) {
      try {
        await notificationsApi.markAsRead(notification.id)
        // 刷新列表
        fetchNotifications(activeTab !== 'all' ? (activeTab as NotificationType) : undefined)
      } catch (error) {
        console.error('Failed to mark as read:', error)
      }
    }

    // TODO: 跳转到相关页面
    console.log('Navigate to:', notification.link || notification.related_post)
  }

  return (
    <div className="space-y-4">
      {/* 通知内容容器 - 使用与 Home.tsx 相同的样式 */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        {/* 顶部标题栏 */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-gray-900">通知</h1>
            {unreadCount > 0 && (
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs font-semibold text-white">
                {unreadCount}
              </span>
            )}
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
            onClick={handleMarkAllAsRead}
          >
            一键已读
          </Button>
        </div>

        {/* 标签页导航 */}
        <div className="flex items-center gap-1 px-6 py-3 border-b overflow-x-auto">
          {[
            { key: 'all', label: '全部', count: notifications.length },
            { key: 'like', label: '点赞', count: counts.like },
            { key: 'comment', label: '评论', count: counts.comment },
            { key: 'follow', label: '关注', count: counts.follow },
            { key: 'system', label: '系统', count: counts.system },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => handleTabChange(tab.key as TabType)}
              className={`
                relative px-4 py-2 text-sm font-medium transition-colors
                ${activeTab === tab.key
                  ? 'text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
                }
              `}
            >
              {tab.label}({tab.count})
              {activeTab === tab.key && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
              )}
            </button>
          ))}
        </div>

        {/* 通知列表 */}
        <div>
          {loading ? (
            <div className="flex items-center justify-center py-12 text-gray-500">
              加载中...
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <Bell className="h-12 w-12 mb-3 opacity-50" />
              <p>暂无通知</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onClick={() => handleNotificationClick(notification)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
