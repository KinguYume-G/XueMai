import React from 'react';
import PostCard from './PostCard';

interface FeedContainerProps {
  className?: string;
}

const FeedContainer: React.FC<FeedContainerProps> = ({ className }) => {
  // 模拟数据 - 根据图片中的内容
  const samplePosts = [
    {
      id: '1',
      author: {
        name: 'Jane Doe APU',
        avatar: '/placeholder-avatar.jpg',
        badge: 'APU'
      },
      content: '成为下一个大型科技创新者\n\n在亚太科技大学(APU),我们不仅仅是教育学生,我们还在培养能够塑造未来数字格局的创新者、领导者和思想家。加入我们,踏上一段激动人心的旅程,释放您的潜力,成为一名科技大师。',
      image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=400&fit=crop',
      likes: 122,
      comments: 15,
      timestamp: '2小时前',
      isLiked: false,
      isBookmarked: false,
      tags: ['#校园生活']
    },
    {
      id: '2',
      author: {
        name: 'John Smith SJTU',
        avatar: '/placeholder-avatar.jpg',
        badge: 'SJTU'
      },
      content: '招聘前端开发实习生!\n\n我们的创业团队正在寻找一名充满激情的前端开发实习生,参与我们的AI教育平台项目。要求熟悉React 和 Tailwind CSS。这是一个绝佳的学习和成长机会!感兴趣的同学请私信。',
      likes: 89,
      comments: 23,
      timestamp: '5小时前',
      isLiked: false,
      isBookmarked: false,
      tags: ['#招募', 'React', 'Tailwind CSS', '实习']
    }
  ];

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
    <div className={`${className}`}>
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
        
        {/* Loading skeleton */}
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    </div>
  );
};

export default FeedContainer;
