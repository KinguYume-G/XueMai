import { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { notificationsApi } from '@/services/api/notifications'
import NotificationPanel from './NotificationPanel'

/**
 * 通知铃铛图标组件
 * 显示在顶部导航栏，点击打开通知模态框
 */
export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  // 获取未读数量
  const fetchUnreadCount = async () => {
    try {
      const data = await notificationsApi.getUnreadCount()
      console.log('🔔 [NotificationBell] getUnreadCount 返回:', data)

      // 健壮的数据提取：处理对象或数组情况
      let count = 0
      if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
        count = data.total || data.unread_count || 0
      }

      console.log('🔔 [NotificationBell] 设置未读数量:', count)
      setUnreadCount(count)
    } catch (error) {
      console.error('❌ [NotificationBell] Failed to fetch unread count:', error)
    }
  }

  // 初始加载和定时轮询（每30秒）
  useEffect(() => {
    fetchUnreadCount()
    const interval = setInterval(fetchUnreadCount, 30000)
    const handleRealtimeNotification = () => setUnreadCount((count) => count + 1)
    window.addEventListener('xuemai:notification', handleRealtimeNotification)
    return () => {
      clearInterval(interval)
      window.removeEventListener('xuemai:notification', handleRealtimeNotification)
    }
  }, [])

  // 点击铃铛打开模态框
  const handleClick = () => {
    setIsOpen(true)
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="relative h-10 w-10 rounded-full"
        onClick={handleClick}
      >
        <Bell className="h-5 w-5" />

        {/* 未读角标 */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-semibold text-white border-2 border-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </Button>

      {/* 通知模态框 */}
      {isOpen && (
        <NotificationPanel
          onClose={() => setIsOpen(false)}
          onNotificationRead={fetchUnreadCount}
        />
      )}
    </>
  )
}
