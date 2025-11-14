import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { X, Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { notificationsApi } from '@/services/api/notifications'
import type { Notification, NotificationType, NotificationCountsByType } from '@/types/notification'
import NotificationItem from './NotificationItem'

interface NotificationPanelProps {
  onClose: () => void
  onNotificationRead?: () => void
}

type TabType = 'all' | NotificationType

/**
 * 通知面板主组件
 * 显示通知列表、标签页、一键已读等功能
 */
export default function NotificationPanel({ onClose, onNotificationRead }: NotificationPanelProps) {
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
  const fetchNotifications = async (type?: NotificationType) => {
    console.log('🔵 [NotificationPanel] fetchNotifications 开始, type:', type)
    setLoading(true)
    try {
      console.log('🔵 [NotificationPanel] 准备调用 API...')
      const data = await notificationsApi.getNotifications({
        type,
        page: 1,
      })

      console.log('🟢 [NotificationPanel] API 返回成功!')
      console.log('🟢 [NotificationPanel] 返回数据 data:', data)
      console.log('🟢 [NotificationPanel] data 类型:', typeof data)
      console.log('🟢 [NotificationPanel] data 是否为数组:', Array.isArray(data))
      console.log('🟢 [NotificationPanel] data.results:', data.results)
      console.log('🟢 [NotificationPanel] data.results 类型:', typeof data.results)
      console.log('🟢 [NotificationPanel] data.results 是否为数组:', Array.isArray(data.results))
      console.log('🟢 [NotificationPanel] data.results 长度:', data.results?.length)

      // 修复：优先检查 data 是否直接是数组
      const notificationsArray = Array.isArray(data) ? data : (data?.results || [])
      console.log('🟠 [NotificationPanel] 准备设置 state, notificationsArray:', notificationsArray)
      console.log('🟠 [NotificationPanel] notificationsArray 长度:', notificationsArray.length)

      setNotifications(notificationsArray)
      console.log('🟠 [NotificationPanel] State 已更新')

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

        console.log('🟠 [NotificationPanel] 计算的未读数量:', calculatedUnreadCount)
        console.log('🟠 [NotificationPanel] 计算的分类统计:', calculatedCounts)

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
      console.error('❌ [NotificationPanel] Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  // 初始加载
  useEffect(() => {
    fetchNotifications()
  }, [])

  // ESC键关闭和body滚动锁定
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    // 禁止body滚动
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleEscape)

    return () => {
      // 恢复body滚动
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleEscape)
    }
  }, [onClose])

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
        // 通知父组件更新未读数量
        if (onNotificationRead) {
          onNotificationRead()
        }
      } catch (error) {
        console.error('Failed to mark as read:', error)
      }
    }

    // TODO: 跳转到相关页面
    console.log('Navigate to:', notification.link || notification.related_post)
  }

  // 调试日志：渲染时的 state
  console.log('🔵 [NotificationPanel] 组件渲染')
  console.log('🔵 [NotificationPanel] notifications state:', notifications)
  console.log('🔵 [NotificationPanel] notifications 长度:', notifications.length)
  console.log('🔵 [NotificationPanel] loading:', loading)
  console.log('🔵 [NotificationPanel] 检查是否显示空状态:', notifications.length === 0)

  return createPortal(
    <>
      {/* 第1层 - 背景遮罩层：半透明黑色背景，覆盖整个屏幕，点击关闭 */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* 第2层 - 居中容器层：使用flexbox将内容居中，点击关闭 */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* 第3层 - 实际内容框：白色通知框，包含所有内容，点击不关闭 */}
        <div
          className="bg-white w-full max-w-[600px] max-h-[80vh] rounded-xl shadow-2xl overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 顶部标题栏 */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div className="flex items-center gap-3">
              <span className="text-lg font-bold">通知</span>
              {unreadCount > 0 && (
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs font-semibold text-white">
                  {unreadCount}
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                className="text-blue-600 hover:text-blue-700"
                onClick={handleMarkAllAsRead}
              >
                一键已读
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full"
                onClick={onClose}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
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

          {/* 通知列表 - 可滚动区域 */}
          <div className="flex-1 overflow-y-auto" style={{ maxHeight: 'calc(80vh - 140px)' }}>
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
    </>,
    document.body
  )
}
