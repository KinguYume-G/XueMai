import { Search, Bell, MessageSquare, Plus, ChevronDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

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


export default function Header() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const displayName = user?.profile?.username ?? user?.username ?? '访客'
  const avatarSrc =
    user?.profile?.avatar_url || user?.profile?.avatar || user?.avatar || undefined
  const avatarFallback = displayName ? displayName.charAt(0).toUpperCase() : 'U'

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="text-lg font-bold text-white">学</span>
          </div>
          <span className="text-lg font-semibold">学脉 | UniPulse Asia</span>
        </div>

        {/* Search Bar */}
        <div className="relative flex-1 max-w-2xl mx-8">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索同学、话题、课程、职位..."
            className="h-11 rounded-full pl-11 pr-4 bg-secondary/50 border-0 focus-visible:ring-1"
          />
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="default"
            className="gap-2 rounded-full h-10 px-6 bg-primary hover:bg-primary/90"
          >
            <Plus className="h-4 w-4" />
            创建
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="relative rounded-full"
            aria-label="通知"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
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
              <div className="flex items-center gap-1 text-sm font-medium">
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

