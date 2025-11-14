import { Search, Bell, MessageSquare, Plus, ChevronDown } from 'lucide-react'
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


export default function Header() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const displayName = user?.profile?.username ?? user?.username ?? '璁垮'
  const avatarSrc =
    user?.profile?.avatar_url || user?.profile?.avatar || user?.avatar || undefined
  const avatarFallback = displayName ? displayName.charAt(0).toUpperCase() : 'U'

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Link to="/" className="inline-flex items-center">
            <img src="/logo.png" alt="UniPulse Asia" className="h-7 md:h-8 w-auto" />
          </Link>
        </div>

        {/* Search Bar */}
        <div className="relative flex-1 max-w-2xl mx-8">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="鎼滅储鍚屽銆佽瘽棰樸€佽绋嬨€佽亴浣?.."
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
            鍒涘缓
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="relative rounded-full"
            aria-label="閫氱煡"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            aria-label="娑堟伅"
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
              <DropdownMenuItem>鎴戠殑涓婚〉</DropdownMenuItem>
              <DropdownMenuItem>涓汉璧勬枡</DropdownMenuItem>
              <DropdownMenuItem>鎴戠殑甯栧瓙</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>璁剧疆</DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  logout()
                  navigate('/login', { replace: true })
                }}
              >
                閫€鍑虹櫥褰?              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

