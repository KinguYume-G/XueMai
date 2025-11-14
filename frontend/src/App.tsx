import { RouterProvider } from 'react-router-dom'
import AuthProvider from '@/components/auth/AuthProvider'
import ChatWidget from '@/components/ai/ChatWidget'
import { router } from './routes'

function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
      <ChatWidget />
    </AuthProvider>
  )
}

export default App

