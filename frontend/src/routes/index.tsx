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
import AITools from '@/pages/AITools'
import AIChat from '@/pages/AIChat'
import NotFound from '@/pages/NotFound'
import SearchResults from '@/pages/SearchResults'
import Protected from '@/components/auth/Protected'
import CreatePost from '@/pages/CreatePost'
import CreateTopic from '@/pages/CreateTopic'
import CreateCommunity from '@/pages/CreateCommunity'
import CreateJob from '@/pages/CreateJob'
import UserProfile from '@/pages/UserProfile'
import PostDetail from '@/pages/PostDetail'
import TopicDetail from '@/pages/TopicDetail'
import StartupDetail from '@/pages/StartupDetail'

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
        element: <CreateCommunity />,
      },
      {
        path: 'communities/:slug',
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
        path: 'users/:id',
        element: <UserProfile />,
      },
      {
        path: 'posts/:id',
        element: <PostDetail />,
      },
      {
        path: 'forums/topics/:id',
        element: <TopicDetail />,
      },
      {
        path: 'startups/:id',
        element: <StartupDetail />,
      },
      {
        path: 'schools/apu',
        element: <Navigate to="/apu" replace />,
      },
      {
        path: 'create/post',
        element: <CreatePost />,
      },
      {
        path: 'create/question',
        element: <CreateTopic />,
      },
      {
        path: 'create/community',
        element: <CreateCommunity />,
      },
      {
        path: 'create/job',
        element: <CreateJob />,
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
