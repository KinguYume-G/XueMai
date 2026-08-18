import { Bot, Briefcase, Home, Menu, Users } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'

const items = [
  { path: '/', label: '主页', icon: Home },
  { path: '/forums', label: '论坛', icon: Menu },
  { path: '/communities', label: '社区', icon: Users },
  { path: '/opportunities', label: '机会', icon: Briefcase },
  { path: '/ai-tools', label: 'AI', icon: Bot },
]

export default function MobileNav() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <nav aria-label="移动端主导航" className="fixed inset-x-0 bottom-0 z-50 grid h-16 grid-cols-5 border-t bg-white/95 backdrop-blur lg:hidden">
      {items.map(({ path, label, icon: Icon }) => {
        const active = path === '/' ? location.pathname === '/' : location.pathname.startsWith(path)
        return (
          <button
            key={path}
            type="button"
            onClick={() => navigate(path)}
            className={`flex flex-col items-center justify-center gap-1 text-xs ${active ? 'text-primary' : 'text-muted-foreground'}`}
          >
            <Icon className="h-5 w-5" />
            <span>{label}</span>
          </button>
        )
      })}
    </nav>
  )
}
