import { Outlet, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import RightAside from '@/components/layout/RightAside'
import { ChatSystem } from '@/components/chat'
import ChatWidget from '@/components/ai/ChatWidget'
import { useAuthStore } from '@/store/authStore'
import { useChatWidgetStore } from '@/store/useChatWidgetStore'

export default function AppLayout() {
  const { pathname } = useLocation()
  const { isAuthenticated } = useAuthStore()
  const isOpen = useChatWidgetStore((state) => state.isOpen)
  const closeChatWidget = useChatWidgetStore((state) => state.close)

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
        <main className="flex-1 ml-64 mr-80 pt-8 pb-12 px-6">
          <div className="max-w-4xl mx-auto">
            <Outlet />
          </div>
        </main>

        <RightAside />
      </div>

      {shouldShowChatWidget ? <ChatWidget /> : null}
      <ChatSystem />
    </div>
  )
}

