import { Bot, Briefcase, Home, Menu, Users } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const items = [
  { path: '/', labelKey: 'sidebar.mobileNav.home', icon: Home },
  { path: '/forums', labelKey: 'sidebar.mobileNav.forums', icon: Menu },
  { path: '/communities', labelKey: 'sidebar.mobileNav.communities', icon: Users },
  { path: '/opportunities', labelKey: 'sidebar.mobileNav.opportunities', icon: Briefcase },
  { path: '/ai-tools', labelKey: 'sidebar.mobileNav.aiTools', icon: Bot },
]

export default function MobileNav() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()

  return (
    <nav aria-label={t('sidebar.mobileNav.ariaLabel')} className="fixed inset-x-0 bottom-0 z-50 grid h-16 grid-cols-5 border-t bg-white/95 backdrop-blur lg:hidden">
      {items.map(({ path, labelKey, icon: Icon }) => {
        const active = path === '/' ? location.pathname === '/' : location.pathname.startsWith(path)
        return (
          <button
            key={path}
            type="button"
            onClick={() => navigate(path)}
            className={`flex flex-col items-center justify-center gap-1 text-xs ${active ? 'text-primary' : 'text-muted-foreground'}`}
          >
            <Icon className="h-5 w-5" />
            <span>{t(labelKey)}</span>
          </button>
        )
      })}
    </nav>
  )
}
