import { Outlet } from 'react-router-dom'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import RightAside from '@/components/layout/RightAside'
import { ChatSystem } from '@/components/chat'

export default function AppLayout() {
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

      <ChatSystem />
    </div>
  )
}

