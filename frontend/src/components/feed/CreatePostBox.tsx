import { useState } from 'react'
import { Image, Video, Link as LinkIcon, Hash } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { postsApi } from '@/services/api/posts'
import { parseApiError } from '@/lib/api/error'
import { useAuthStore } from '@/store/authStore'

interface CreatePostBoxProps {
  onPostCreated?: () => void
}

export default function CreatePostBox({ onPostCreated }: CreatePostBoxProps) {
  const { t } = useTranslation()
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const user = useAuthStore((state) => state.user)

  const handlePublish = async () => {
    if (!content.trim()) return

    try {
      setLoading(true)
      setError(null)

      const newPost = await postsApi.createPost({
        body: content.trim(),
        visibility: 'public',
        is_published: true,
      })

      // 调试日志（开发环境）
      if (import.meta.env.DEV) {
        console.log('[CreatePost] Post created:', newPost)
      }

      setContent('')
      
      // 通知父组件，父组件会重新拉取 Feed 确保数据一致性
      if (onPostCreated) {
        onPostCreated()
      }
    } catch (err) {
      console.error('Failed to create post:', err)
      setError(parseApiError(err))
    } finally {
      setLoading(false)
    }
  }

  const avatarSrc = user?.profile?.avatar_url || user?.avatar
  const avatarFallback = user?.username?.charAt(0).toUpperCase() || 'U'

  return (
    <Card className="border shadow-sm">
      <div className="p-4">
        <div className="flex gap-3">
          <Avatar className="h-10 w-10">
            {avatarSrc ? <AvatarImage src={avatarSrc} /> : null}
            <AvatarFallback>{avatarFallback}</AvatarFallback>
          </Avatar>
          
          <div className="flex-1">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={t('feed.createBox.placeholder')}
              className="w-full resize-none border-0 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-0 min-h-[60px]"
              disabled={loading}
            />
            
            {error && (
              <div className="text-xs text-destructive mt-2">{error}</div>
            )}
            
            <div className="flex items-center justify-between mt-3 pt-3 border-t">
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label={t('feed.createBox.addImage')}
                  disabled={loading}
                >
                  <Image className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label={t('feed.createBox.addVideo')}
                  disabled={loading}
                >
                  <Video className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label={t('feed.createBox.addLink')}
                  disabled={loading}
                >
                  <LinkIcon className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label={t('feed.createBox.addTopic')}
                  disabled={loading}
                >
                  <Hash className="h-5 w-5" />
                </Button>
              </div>

              <Button
                onClick={handlePublish}
                disabled={!content.trim() || loading}
                className="rounded-full px-6 h-9 bg-primary hover:bg-primary/90"
              >
                {loading ? t('feed.createBox.publishing') : t('feed.createBox.publish')}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

