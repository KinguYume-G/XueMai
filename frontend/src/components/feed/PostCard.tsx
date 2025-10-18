import React, { useState } from 'react';
import { 
  ThumbsUp, 
  MessageSquare, 
  Bookmark, 
  Share, 
  MoreHorizontal,
  Heart
} from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import TagBadge from './TagBadge';
import { User } from 'lucide-react';

interface Post {
  id: string;
  author: {
    name: string;
    avatar: string;
    badge?: string;
  };
  content: string;
  image?: string;
  likes: number;
  comments: number;
  timestamp: string;
  isLiked: boolean;
  isBookmarked: boolean;
  tags?: string[];
}

interface PostCardProps {
  post: Post;
  onLike?: (postId: string) => void;
  onBookmark?: (postId: string) => void;
  onShare?: (postId: string) => void;
  onComment?: (postId: string) => void;
}

const PostCard: React.FC<PostCardProps> = ({
  post,
  onLike,
  onBookmark,
  onShare,
  onComment
}) => {
  const [isLiked, setIsLiked] = useState(post.isLiked);
  const [isBookmarked, setIsBookmarked] = useState(post.isBookmarked);
  const [likesCount, setLikesCount] = useState(post.likes);

  const handleLike = () => {
    const newLikedState = !isLiked;
    setIsLiked(newLikedState);
    setLikesCount(prev => newLikedState ? prev + 1 : prev - 1);
    onLike?.(post.id);
  };

  const handleBookmark = () => {
    const newBookmarkedState = !isBookmarked;
    setIsBookmarked(newBookmarkedState);
    onBookmark?.(post.id);
  };

  const handleShare = () => {
    onShare?.(post.id);
  };

  const handleComment = () => {
    onComment?.(post.id);
  };

  return (
    <Card className="mb-6 hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Avatar className="h-10 w-10">
              <AvatarImage src={post.author.avatar} alt={post.author.name} />
              <AvatarFallback>
                <User className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-gray-900">{post.author.name}</span>
                {post.author.badge && (
                  <Badge variant="secondary" className="text-xs">
                    {post.author.badge}
                  </Badge>
                )}
              </div>
              <span className="text-sm text-gray-500">{post.timestamp}</span>
            </div>
          </div>
          
          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex items-center space-x-2">
              {post.tags.slice(0, 1).map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>举报</DropdownMenuItem>
              <DropdownMenuItem>复制链接</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>关注用户</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Content */}
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {post.content.split('\n')[0]}
          </h3>
          <p className="text-gray-900 leading-relaxed whitespace-pre-wrap">
            {post.content.split('\n').slice(1).join('\n')}
          </p>
          
          {/* Tags */}
          {post.tags && post.tags.length > 1 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {post.tags.slice(1).map((tag, index) => (
                <TagBadge
                  key={index}
                  label={tag}
                  variant={index % 3 === 0 ? 'blue' : index % 3 === 1 ? 'green' : 'yellow'}
                  onClick={() => console.log(`Clicked tag: ${tag}`)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Image */}
        {post.image && (
          <div className="mb-4">
            <img
              src={post.image}
              alt="Post content"
              className="w-full max-h-[400px] object-cover rounded-lg"
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center space-x-6">
            {/* Like */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLike}
              className={`flex items-center space-x-2 ${
                isLiked ? 'text-blue-600' : 'text-gray-600'
              }`}
            >
              {isLiked ? (
                <Heart className="h-4 w-4 fill-current" />
              ) : (
                <ThumbsUp className="h-4 w-4" />
              )}
              <span className="text-sm">{likesCount}</span>
            </Button>

            {/* Comment */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleComment}
              className="flex items-center space-x-2 text-gray-600"
            >
              <MessageSquare className="h-4 w-4" />
              <span className="text-sm">{post.comments}</span>
            </Button>

            {/* Bookmark */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBookmark}
              className={`${
                isBookmarked ? 'text-blue-600' : 'text-gray-600'
              }`}
            >
              <Bookmark className={`h-4 w-4 ${isBookmarked ? 'fill-current' : ''}`} />
            </Button>
          </div>

          {/* Share */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleShare}
            className="text-gray-600"
          >
            <Share className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PostCard;
