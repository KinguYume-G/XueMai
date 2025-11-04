import { Home, GraduationCap, Users, Briefcase, Bot, BookmarkIcon, Globe, Moon, Settings, MessageCircle, Plane } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

interface NavItem {
  icon: React.ElementType
  label: string
  path: string
}

const navigationItems: NavItem[] = [
  { icon: Home, label: '主页', path: '/' },
  { icon: GraduationCap, label: '专业论坛', path: '/forums' },
  { icon: Users, label: '社区', path: '/community' },
  { icon: Plane, label: '交换项目', path: '/exchange' },
  { icon: Briefcase, label: '实习 & 机会', path: '/internships' },
  { icon: Bot, label: 'AI 真具箱', path: '/ai-tools' },
  { icon: BookmarkIcon, label: '收藏', path: '/bookmarks' },
  { icon: GraduationCap, label: '关于 APU', path: '/about-apu' },
]

export default function Sidebar() {
  const [language, setLanguage] = useState('中')
  const [isDark, setIsDark] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const languages = ['中', 'EN', 'MY']

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 border-r bg-white overflow-y-auto">
      <nav className="flex flex-col h-full p-4">
        {/* Navigation Items */}
        <div className="flex-1 space-y-1">
          {navigationItems.map((item, index) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path ||
              (item.path !== '/' && location.pathname.startsWith(item.path))
            return (
              <Button
                key={index}
                variant={isActive ? "secondary" : "ghost"}
                className={`w-full justify-start gap-3 h-11 px-4 ${
                  isActive ? 'bg-secondary font-medium' : ''
                }`}
                onClick={() => navigate(item.path)}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Button>
            )
          })}
        </div>

        {/* Bottom Section */}
        <div className="mt-auto space-y-2">
          <Separator className="my-2" />
          
          {/* Language Selector */}
          <div className="flex gap-1 p-1 bg-secondary rounded-lg">
            {languages.map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  language === lang
                    ? 'bg-white text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {lang}
              </button>
            ))}
          </div>

          {/* Theme and Settings */}
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="flex-1"
              onClick={() => setIsDark(!isDark)}
              aria-label="切换主题"
            >
              {isDark ? <Moon className="h-5 w-5" /> : <Globe className="h-5 w-5" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="flex-1"
              aria-label="设置"
            >
              <Settings className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="flex-1"
              aria-label="反馈"
            >
              <MessageCircle className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </nav>
    </aside>
  )
}

