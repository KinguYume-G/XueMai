import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './AppLayout'
import Home from '@/pages/Home'
import AuthLoginPage from '@/pages/AuthLoginPage'
import AuthRegisterPage from '@/pages/AuthRegisterPage'
import Forums from '@/pages/Forums'
import Communities from '@/pages/Communities'
import Community from '@/pages/Community'
import ExchangeListPage from '@/pages/Exchange'
import ExchangeDetailPage from '@/pages/Exchange/Detail'
import InternshipsListPage from '@/pages/Internships'
import InternshipDetailPage from '@/pages/Internships/Detail'
import Opportunities from '@/pages/Opportunities'
import Bookmarks from '@/pages/Bookmarks'
import Notifications from '@/pages/Notifications'
import AboutAPU from '@/pages/AboutAPU'
import ComingSoon from '@/pages/ComingSoon'
import AITools from '@/pages/AITools'
import AIChat from '@/pages/AIChat'
import NotFound from '@/pages/NotFound'
import SearchResults from '@/pages/SearchResults'
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
        path: 'communities/create',
        element: <ComingSoon title="创建社区" message="社区创建功能正在开发中" />,
      },
      {
        path: 'communities/:id',
        element: <Community />,
      },
      {
        path: 'community',
        element: <Community />,
      },
      {
        path: 'exchange',
        element: <ExchangeListPage />,
      },
      {
        path: 'exchange/:id',
        element: <ExchangeDetailPage />,
      },
      {
        path: 'exchange-programs',
        element: <Navigate to="/exchange" replace />,
      },
      {
        path: 'exchange-programs/:id',
        element: <ExchangeDetailPage />,
      },
      {
        path: 'internships',
        element: <InternshipsListPage />,
      },
      {
        path: 'internships/:id',
        element: <InternshipDetailPage />,
      },
      {
        path: 'opportunities',
        element: <Opportunities />,
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
        path: 'search',
        element: <SearchResults />,
      },
      {
        path: 'schools/apu',
        element: <Navigate to="/apu" replace />,
      },
      // Coming Soon pages
      {
        path: 'create/post',
        element: <ComingSoon title="发布帖子" message="帖子发布功能正在开发中" />,
      },
      {
        path: 'create/question',
        element: <ComingSoon title="提出问题" message="问答功能正在开发中" />,
      },
      {
        path: 'create/community',
        element: <ComingSoon title="创建社区" message="社区创建功能正在开发中" />,
      },
      {
        path: 'create/job',
        element: <ComingSoon title="发布职位" message="职位发布功能正在开发中" />,
      },
      {
        path: 'ai-tools',
        element: <AITools />,
      },
      {
        path: 'ai',
        element: <Navigate to="/ai-tools" replace />,
      },
      {
        path: 'ai-chat/:functionId',
        element: <AIChat />,
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
    element: <NotFound />,
  },
])
