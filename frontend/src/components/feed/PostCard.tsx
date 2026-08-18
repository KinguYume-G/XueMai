import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Heart, MessageCircle, Share2, MoreHorizontal } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { postsApi } from '@/services/api/posts'
import type { Post } from '@/types/api'

interface PostCardProps {
  post: Post
}

export default function PostCard({ post }: PostCardProps) {
  const [isLiked, setIsLiked] = useState(post.is_liked)
  const [likes, setLikes] = useState(post.likes_count)
  const [liking, setLiking] = useState(false)

  const handleLike = async () => {
    if (liking) return
    
    try {
      setLiking(true)
      const newLikedState = !isLiked
      
      if (newLikedState) {
        await postsApi.likePost(post.id)
        setLikes(likes + 1)
      } else {
        await postsApi.unlikePost(post.id)
        setLikes(likes - 1)
      }
      
      setIsLiked(newLikedState)
    } catch (error) {
      console.error('Failed to toggle like:', error)
    } finally {
      setLiking(false)
    }
  }

  // 格式化时间
  const formatTime = (dateString: string) => {
    if (!dateString) return '未知时间'
    
    try {
      const date = new Date(dateString)
      // 检查日期是否有效
      if (isNaN(date.getTime())) {
        return '未知时间'
      }
      
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      
      // 避免负数（未来时间）
      if (diffMs < 0) {
        return new Intl.DateTimeFormat('zh-CN', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        }).format(date)
      }
      
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      
      if (diffMins < 1) return '刚刚'
      if (diffMins < 60) return `${diffMins}分钟前`
      if (diffHours < 24) return `${diffHours}小时前`
      if (diffDays < 7) return `${diffDays}天前`
      
      // 超过7天，使用 Intl.DateTimeFormat 格式化日期
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }).format(date)
    } catch (error) {
      console.error('Failed to format date:', dateString, error)
      return '未知时间'
    }
  }

  const authorName = post.author_username || '未知用户'
  const authorAvatar = post.author_avatar
  const authorFallback = authorName.charAt(0).toUpperCase()

  return (
    <Card className="border shadow-sm overflow-hidden">
      <div className="p-4">
        {/* Author Info */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex gap-3">
            <Avatar className="h-10 w-10">
              {authorAvatar ? <AvatarImage src={authorAvatar} /> : null}
              <AvatarFallback>{authorFallback}</AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{authorName}</span>
                {post.visibility !== 'public' && (
                  <Badge variant="secondary" className="text-xs px-2 py-0">
                    {post.visibility === 'followers' ? '仅关注者' : 
                     post.visibility === 'university' ? '同校可见' : '私密'}
                  </Badge>
                )}
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                {formatTime(post.created_at)}
              </div>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full"
            aria-label="更多选项"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="space-y-3">
          <Link to={`/posts/${post.id}`} className="block space-y-3 hover:opacity-90">
            {post.title && (
              <h3 className="font-semibold text-lg">{post.title}</h3>
            )}
            <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
              {post.body}
            </p>
          </Link>

          {/* Tags */}
          {post.tags_data && post.tags_data.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {post.tags_data.map((tag) => (
                <Badge
                  key={tag.id}
                  variant="secondary"
                  className="rounded-md px-3 py-1 text-xs font-medium hover:bg-secondary/80 cursor-pointer"
                >
                  #{tag.name}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Image */}
      {post.image_url && (
        <div className="relative w-full aspect-[2/1] bg-muted">
          <img
            src={post.image_url}
            alt={post.title || '帖子图片'}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-6 px-4 py-3 border-t">
        <button
          onClick={handleLike}
          disabled={liking}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group disabled:opacity-50"
        >
          <Heart
            className={`h-5 w-5 ${
              isLiked ? 'fill-primary text-primary' : 'group-hover:scale-110 transition-transform'
            }`}
          />
          <span className={isLiked ? 'text-primary font-medium' : ''}>
            {likes}
          </span>
        </button>

        <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors">
          <MessageCircle className="h-5 w-5" />
          <span>{post.comments_count}</span>
        </button>

        <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors ml-auto">
          <Share2 className="h-5 w-5" />
        </button>
      </div>
    </Card>
  )
}

