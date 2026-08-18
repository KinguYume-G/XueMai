import { Outlet, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import RightAside from '@/components/layout/RightAside'
import { ChatSystem } from '@/components/chat'
import ChatWidget from '@/components/ai/ChatWidget'
import { ToastContainer } from '@/components/ui/toast'
import MobileNav from '@/components/layout/MobileNav'
import { useAuthStore } from '@/store/authStore'
import { useChatWidgetStore } from '@/store/useChatWidgetStore'
import { useToastStore } from '@/store/useToastStore'

export default function AppLayout() {
  const { pathname } = useLocation()
  const { isAuthenticated } = useAuthStore()
  const isOpen = useChatWidgetStore((state) => state.isOpen)
  const closeChatWidget = useChatWidgetStore((state) => state.close)
  const toasts = useToastStore((state) => state.toasts)
  const removeToast = useToastStore((state) => state.removeToast)

  const isHomeRoute = pathname === '/home' || pathname === '/'
  const shouldShowChatWidget = isAuthenticated && isHomeRoute

  useEffect(() => {
    if ((!isHomeRoute || !isAuthenticated) && isOpen) {
      closeChatWidget()
    }
  }, [isHomeRoute, isAuthenticated, isOpen, closeChatWidget])

  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      <Header />
      <div className="flex">
        <Sidebar />

        {/* Main Content */}
        <main className="ml-0 flex-1 px-4 pb-20 pt-6 sm:px-6 lg:ml-64 lg:pb-12 lg:pt-8 xl:mr-80">
          <div className="max-w-4xl mx-auto">
            <Outlet />
          </div>
        </main>

        <RightAside />
      </div>

      {shouldShowChatWidget ? <ChatWidget /> : null}
      <ChatSystem />
      <MobileNav />
      
      {/* Toast通知 */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
