import { useEffect, useRef, type ReactNode } from 'react'
import { useAuthStore } from '@/store/authStore'
import { getAccessToken } from '@/lib/auth/token'

type AuthProviderProps = {
  children: ReactNode
}

/**
 * Authentication bootstrapper that restores user sessions before rendering the app shell.
 */
export default function AuthProvider({ children }: AuthProviderProps) {
  const fetchMe = useAuthStore((state) => state.fetchMe)
  const isReady = useAuthStore((state) => state.isReady)
  const hasChecked = useRef(false)

  useEffect(() => {
    // 确保只执行一次
    if (hasChecked.current) return
    hasChecked.current = true

    const initAuth = async () => {
      const token = getAccessToken()
      
      if (token) {
        try {
          // 有 token，尝试获取用户信息
          await fetchMe()
        } catch (error) {
          // Token 无效，fetchMe 已经处理了清理工作（包括设置 isReady=true）
          console.error('Failed to restore session:', error)
        }
      } else {
        // 没有 token，直接标记为 ready
        await fetchMe() // fetchMe 会设置 isReady=true
      }
    }

    initAuth()
  }, [fetchMe]) // 依赖 fetchMe

  // 等待认证状态初始化完成
  if (!isReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return <>{children}</>
}


