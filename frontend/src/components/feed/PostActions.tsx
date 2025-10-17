import React, { useState } from 'react';
import { 
  ThumbsUp, 
  MessageSquare, 
  Bookmark, 
  Share, 
  Heart
} from 'lucide-react';
import { Button } from '../ui/button';

interface PostActionsProps {
  postId: string;
  likes: number;
  comments: number;
  isLiked: boolean;
  isBookmarked: boolean;
  onLike?: (postId: string) => void;
  onBookmark?: (postId: string) => void;
  onShare?: (postId: string) => void;
  onComment?: (postId: string) => void;
  className?: string;
}

const PostActions: React.FC<PostActionsProps> = ({
  postId,
  likes,
  comments,
  isLiked,
  isBookmarked,
  onLike,
  onBookmark,
  onShare,
  onComment,
  className
}) => {
  const [likesCount, setLikesCount] = useState(likes);
  const [liked, setLiked] = useState(isLiked);
  const [bookmarked, setBookmarked] = useState(isBookmarked);

  const handleLike = () => {
    const newLikedState = !liked;
    setLiked(newLikedState);
    setLikesCount(prev => newLikedState ? prev + 1 : prev - 1);
    onLike?.(postId);
  };

  const handleBookmark = () => {
    const newBookmarkedState = !bookmarked;
    setBookmarked(newBookmarkedState);
    onBookmark?.(postId);
  };

  const handleShare = () => {
    onShare?.(postId);
  };

  const handleComment = () => {
    onComment?.(postId);
  };

  return (
    <div className={`flex items-center justify-between pt-3 border-t border-gray-100 ${className}`}>
      <div className="flex items-center space-x-6">
        {/* Like */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLike}
          className={`flex items-center space-x-2 transition-colors ${
            liked ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
          }`}
        >
          {liked ? (
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
          className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
        >
          <MessageSquare className="h-4 w-4" />
          <span className="text-sm">{comments}</span>
        </Button>

        {/* Bookmark */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBookmark}
          className={`transition-colors ${
            bookmarked ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
          }`}
        >
          <Bookmark className={`h-4 w-4 ${bookmarked ? 'fill-current' : ''}`} />
        </Button>
      </div>

      {/* Share */}
      <Button
        variant="ghost"
        size="sm"
        onClick={handleShare}
        className="text-gray-600 hover:text-blue-600 transition-colors"
      >
        <Share className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default PostActions;
