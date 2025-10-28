import { useState } from 'react'
import { Heart, MessageCircle, Share2, MoreHorizontal } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { Post } from '@/types/post'

interface PostCardProps {
  post: Post
}

export default function PostCard({ post }: PostCardProps) {
  const [isLiked, setIsLiked] = useState(post.isLiked)
  const [likes, setLikes] = useState(post.likes)

  const handleLike = () => {
    setIsLiked(!isLiked)
    setLikes(isLiked ? likes - 1 : likes + 1)
  }

  return (
    <Card className="border shadow-sm overflow-hidden">
      <div className="p-4">
        {/* Author Info */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex gap-3">
            <Avatar className="h-10 w-10">
              <AvatarImage src={post.author.avatar} />
              <AvatarFallback>{post.author.name[0]}</AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{post.author.name}</span>
                {post.author.schoolBadge && (
                  <Badge variant="secondary" className="text-xs px-2 py-0">
                    {post.author.schoolBadge} {post.author.school}
                  </Badge>
                )}
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                {post.timestamp}
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
          {post.title && (
            <h3 className="font-semibold text-lg">{post.title}</h3>
          )}
          <p className="text-sm leading-relaxed text-foreground/90">
            {post.content}
          </p>
          
          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="rounded-md px-3 py-1 text-xs font-medium hover:bg-secondary/80 cursor-pointer"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Image */}
      {post.image && (
        <div className="relative w-full aspect-[2/1] bg-muted">
          <img
            src={post.image}
            alt={post.title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-6 px-4 py-3 border-t">
        <button
          onClick={handleLike}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group"
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
          <span>{post.comments}</span>
        </button>

        <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors ml-auto">
          <Share2 className="h-5 w-5" />
        </button>
      </div>
    </Card>
  )
}

