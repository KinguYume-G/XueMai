import React from 'react';
import CreatePostBox from './CreatePostBox';
import PostCard from './PostCard';
import FeedTabs from './FeedTabs';

interface FeedContainerProps {
  className?: string;
}

const FeedContainer: React.FC<FeedContainerProps> = ({ className }) => {
  // 模拟数据
  const samplePosts = [
    {
      id: '1',
      author: {
        name: '张小明',
        avatar: '/placeholder-avatar.jpg',
        badge: '关注生活'
      },
      content: '今天在APU的图书馆学习了一整天，环境真的很棒！推荐给所有需要安静学习环境的同学。\n\n#APU学习 #图书馆',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=400&fit=crop',
      likes: 122,
      comments: 15,
      timestamp: '2小时前',
      isLiked: false,
      isBookmarked: false,
      tags: ['APU学习', '图书馆']
    },
    {
      id: '2',
      author: {
        name: '李华',
        avatar: '/placeholder-avatar.jpg',
        badge: '实习经验'
      },
      content: '分享一些在马来西亚找实习的经验：\n\n1. 准备好英文简历\n2. 多关注LinkedIn上的职位\n3. 参加学校的career fair\n4. 主动联系HR\n\n希望对大家有帮助！',
      likes: 89,
      comments: 23,
      timestamp: '4小时前',
      isLiked: true,
      isBookmarked: false,
      tags: ['实习', '马来西亚', '求职经验']
    },
    {
      id: '3',
      author: {
        name: '王小红',
        avatar: '/placeholder-avatar.jpg',
        badge: '交换项目'
      },
      content: '早稻田大学的交换项目申请已经开始了！有想去的同学可以联系我，我可以分享一些申请经验。',
      likes: 67,
      comments: 8,
      timestamp: '6小时前',
      isLiked: false,
      isBookmarked: true,
      tags: ['早稻田大学', '交换项目', '申请经验']
    }
  ];

  const handlePost = (content: string, images: File[]) => {
    console.log('New post:', { content, images });
    // 这里会调用API创建新帖子
  };

  const handleLike = (postId: string) => {
    console.log('Like post:', postId);
  };

  const handleBookmark = (postId: string) => {
    console.log('Bookmark post:', postId);
  };

  const handleShare = (postId: string) => {
    console.log('Share post:', postId);
  };

  const handleComment = (postId: string) => {
    console.log('Comment on post:', postId);
  };

  return (
    <div className={`max-w-2xl mx-auto ${className}`}>
      {/* Create Post Box */}
      <CreatePostBox
        onPost={handlePost}
        userAvatar="/placeholder-avatar.jpg"
        userName="当前用户"
      />

      {/* Posts Feed */}
      <div className="space-y-6">
        {samplePosts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            onLike={handleLike}
            onBookmark={handleBookmark}
            onShare={handleShare}
            onComment={handleComment}
          />
        ))}
      </div>
    </div>
  );
};

export default FeedContainer;
