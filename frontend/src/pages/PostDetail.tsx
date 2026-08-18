import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Heart, MessageCircle, Bookmark, Eye, Pencil, Trash2 } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import SkeletonCard from '@/components/common/SkeletonCard'
import ErrorState from '@/components/common/ErrorState'
import ConfirmDialog from '@/components/common/ConfirmDialog'
import { parseApiError } from '@/lib/api/error'
import { postsApi } from '@/services/api/posts'
import { useAuthStore } from '@/store/authStore'
import type { PostApiRecord } from '@/types/api'

export default function PostDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const currentUser = useAuthStore((state) => state.user)
  const [post, setPost] = useState<PostApiRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

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

  const isOwner = Boolean(post && currentUser && post.author.id === currentUser.id)

  const handleDelete = async () => {
    if (!post) return
    setDeleting(true)
    setDeleteError(null)
    try {
      await postsApi.deletePost(post.id)
      navigate('/')
    } catch (reason) {
      // A stale UI could still show the delete button for a 403; surface the
      // error instead of crashing and let the user retry or back out.
      setDeleteError(parseApiError(reason))
      setDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

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
      <div className="flex items-center justify-between gap-2">
        <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          返回
        </Button>
        {isOwner && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/posts/${post.id}/edit`)}>
              <Pencil className="h-4 w-4" />
              编辑
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="gap-2 text-red-600 hover:text-red-700"
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 className="h-4 w-4" />
              删除
            </Button>
          </div>
        )}
      </div>

      {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}

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

      {showDeleteConfirm && (
        <ConfirmDialog
          title="确定删除这篇帖子？"
          description="删除后无法恢复，帖子的评论和互动记录也会一并移除。"
          confirmLabel="删除"
          confirming={deleting}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </div>
  )
}
