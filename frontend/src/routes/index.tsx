import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './AppLayout'
import Home from '@/pages/Home'
import AuthLoginPage from '@/pages/AuthLoginPage'
import AuthRegisterPage from '@/pages/AuthRegisterPage'
import Forums from '@/pages/Forums'
import Communities from '@/pages/Communities'
import ExchangePrograms from '@/pages/ExchangePrograms'
import Opportunities from '@/pages/Opportunities'
import Bookmarks from '@/pages/Bookmarks'
import Notifications from '@/pages/Notifications'
import AboutAPU from '@/pages/AboutAPU'
import AIAssistant from '@/pages/AIAssistant'
import CreateContent from '@/pages/CreateContent'
import InternshipDetailPage from '@/pages/Internships/Detail'
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
      {
        path: 'forums',
        element: <Forums />,
      },
      {
        path: 'communities',
        element: <Communities />,
      },
      {
        path: 'exchange',
        element: <ExchangePrograms />,
      },
      {
        path: 'opportunities',
        element: <Opportunities />,
      },
      {
        path: 'internships/:id',
        element: <InternshipDetailPage />,
      },
      {
        path: 'bookmarks',
        element: <Bookmarks />,
      },
      {
        path: 'notifications',
        element: <Notifications />,
      },
      {
        path: 'apu',
        element: <AboutAPU />,
      },
      {
        path: 'create/post',
        element: <CreateContent kind="post" />,
      },
      {
        path: 'create/question',
        element: <CreateContent kind="question" />,
      },
      {
        path: 'create/community',
        element: <CreateContent kind="community" />,
      },
      {
        path: 'create/job',
        element: <CreateContent kind="job" />,
      },
      {
        path: 'ai-tools',
        element: <AIAssistant />,
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
