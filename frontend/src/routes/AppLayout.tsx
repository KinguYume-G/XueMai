import { Outlet } from 'react-router-dom'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import RightPanel from '@/components/layout/RightPanel'
import FloatingAIButton from '@/components/common/FloatingAIButton'

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-[#F5F7FB]">
      <Header />
      
      <div className="flex">
        <Sidebar />
        
        {/* Main Content */}
        <main className="flex-1 ml-64 mr-80 pt-6 pb-12 px-6">
          <div className="max-w-3xl mx-auto">
            <Outlet />
          </div>
        </main>
        
        <RightPanel />
      </div>
      
      <FloatingAIButton />
    </div>
  )
}

