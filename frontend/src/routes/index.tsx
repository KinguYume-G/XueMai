import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './AppLayout'
import Home from '@/pages/Home'
import AuthLoginPage from '@/pages/AuthLoginPage'
import AuthRegisterPage from '@/pages/AuthRegisterPage'
import Protected from '@/components/auth/Protected'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <Protected>
        <AppLayout />
      </Protected>
    ),
    children: [
      {
        index: true,
        element: <Home />,
      },
    ],
  },
  {
    path: '/login',
    element: <AuthLoginPage />,
  },
  {
    path: '/register',
    element: <AuthRegisterPage />,
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

