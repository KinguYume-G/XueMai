import { Home, GraduationCap, Users, Briefcase, Bot, BookmarkIcon, Plane } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

interface NavItem {
  icon: React.ElementType
  label: string
  path: string
}

const navigationItems: NavItem[] = [
  { icon: Home, label: '主页', path: '/' },
  { icon: GraduationCap, label: '专业论坛', path: '/forums' },
  { icon: Users, label: '社区', path: '/communities' },
  { icon: Plane, label: '交换项目', path: '/exchange' },
  { icon: Briefcase, label: '实习 & 机会', path: '/opportunities' },
  { icon: Bot, label: 'AI 工具箱', path: '/ai-tools' },
  { icon: BookmarkIcon, label: '收藏', path: '/bookmarks' },
  { icon: GraduationCap, label: '关于 APU', path: '/apu' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { i18n } = useTranslation()

  const currentLanguage = i18n.language
  const languages = [
    { code: 'zh', label: '中' },
    { code: 'en', label: 'EN' }
  ]

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang)
    localStorage.setItem('language', lang)
  }

  return (
    <aside className="fixed bottom-0 left-0 top-16 hidden w-64 overflow-y-auto border-r bg-white lg:block">
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
          
          {/* Language Selector - 新版本（只有中/EN） */}
          <div className="flex gap-1 p-1 bg-secondary rounded-lg">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  currentLanguage === lang.code
                    ? 'bg-white text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>
      </nav>
    </aside>
  )
}

