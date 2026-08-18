import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Heart, MessageCircle, Bookmark, Eye } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import { parseApiError } from '@/lib/api/error'
import { postsApi } from '@/services/api/posts'
import type { PostApiRecord } from '@/types/api'

export default function PostDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [post, setPost] = useState<PostApiRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!id) return
    setLoading(true)
    setError(null)
    postsApi
      .getPost(Number(id))
      .then(setPost)
      .catch((reason) => setError(parseApiError(reason)))
      .finally(() => setLoading(false))
  }

  useEffect(load, [id])

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonCard count={1} />
      </div>
    )
  }

  if (error || !post) {
    return (
      <div className="space-y-4">
        <Card className="border shadow-sm">
          <CardContent className="p-6">
            <ErrorState message={error || '帖子不存在'} onRetry={load} />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回
      </Button>

      <Card className="border shadow-sm">
        <CardContent className="p-6 space-y-4">
          <Link to={`/users/${post.author.id}`} className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback>{post.author.username.slice(0, 1).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <div className="font-medium">{post.author.username}</div>
              <div className="text-xs text-muted-foreground">{new Date(post.created_at).toLocaleString('zh-CN')}</div>
            </div>
          </Link>

          {post.title && <h1 className="text-2xl font-bold">{post.title}</h1>}

          {post.image_url && (
            <img src={post.image_url} alt={post.title || '帖子图片'} className="max-h-[480px] w-full rounded-lg object-cover" />
          )}

          <div className="whitespace-pre-wrap text-sm text-muted-foreground">{post.body}</div>

          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary">#{tag.name}</Badge>
              ))}
            </div>
          )}

          <Separator />

          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            <span className="flex items-center gap-2"><Heart className="h-4 w-4" />{post.likes_count}</span>
            <span className="flex items-center gap-2"><MessageCircle className="h-4 w-4" />{post.comments_count}</span>
            <span className="flex items-center gap-2"><Bookmark className="h-4 w-4" />{post.bookmarks_count}</span>
            <span className="flex items-center gap-2"><Eye className="h-4 w-4" />{post.views_count}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
