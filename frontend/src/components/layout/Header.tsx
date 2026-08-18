import { Search, MessageSquare, Plus, ChevronDown } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useAuthStore } from '@/store/authStore'
import { NotificationBell } from '@/components/notifications'


export default function Header() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const displayName = user?.profile?.username ?? user?.username ?? '访客'
  const avatarSrc =
    user?.profile?.avatar_url || user?.profile?.avatar || user?.avatar || undefined
  const avatarFallback = displayName ? displayName.charAt(0).toUpperCase() : 'U'

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const query = searchQuery.trim()
    if (query.length >= 2) {
      navigate(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="flex h-16 items-center justify-between px-3 sm:px-6">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Link to="/" className="inline-flex items-center">
            <img src="/logo.png" alt="UniPulse Asia" className="h-7 md:h-8 w-auto" />
          </Link>
          <span className="hidden text-lg font-semibold xl:inline">学脉 | UniPulse Asia</span>
        </div>

        {/* Search Bar */}
        <form onSubmit={submitSearch} className="relative mx-4 hidden max-w-2xl flex-1 md:block xl:mx-8">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            aria-label="搜索学脉"
            placeholder="搜索同学、话题、课程、职位..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            className="h-11 rounded-full pl-11 pr-4 bg-secondary/50 border-0 focus-visible:ring-1"
          />
        </form>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger className="hidden h-10 items-center gap-2 rounded-full bg-primary px-4 font-medium text-white transition-colors hover:bg-primary/90 sm:flex xl:px-6">
              <Plus className="h-4 w-4" />
              创建
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuItem onClick={() => navigate('/create/post')}>
                <span className="mr-2">📝</span>
                发布帖子
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/create/question')}>
                <span className="mr-2">❓</span>
                提出问题
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/create/community')}>
                <span className="mr-2">🌐</span>
                创建社区
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/create/job')}>
                <span className="mr-2">💼</span>
                发布职位
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <NotificationBell />

          <Button
            variant="ghost"
            size="icon"
            className="hidden rounded-full sm:inline-flex"
            aria-label="消息"
          >
            <MessageSquare className="h-5 w-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-full px-2 py-1 hover:bg-secondary/80">
              <Avatar className="h-9 w-9">
                {avatarSrc ? <AvatarImage src={avatarSrc} /> : null}
                <AvatarFallback>{avatarFallback}</AvatarFallback>
              </Avatar>
              <div className="hidden items-center gap-1 text-sm font-medium md:flex">
                <span>{displayName}</span>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuItem>我的主页</DropdownMenuItem>
              <DropdownMenuItem>个人资料</DropdownMenuItem>
              <DropdownMenuItem>我的帖子</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>设置</DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  logout()
                  navigate('/login', { replace: true })
                }}
              >
                退出登录
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
