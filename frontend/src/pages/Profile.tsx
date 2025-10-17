import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import ProfileCard from '../components/profile/ProfileCard';
import PostCard from '../components/feed/PostCard';

const Profile: React.FC = () => {
  const [activeTab, setActiveTab] = useState('posts');

  // 模拟用户数据
  const userData = {
    name: '张小明',
    avatar: '/placeholder-avatar.jpg',
    email: 'zhangxiaoming@example.com',
    phone: '+86 138 0000 0000',
    location: '马来西亚，吉隆坡',
    joinDate: '2023年9月',
    bio: 'APU计算机科学专业学生，热爱编程和技术分享。目前在马来西亚学习，希望与更多同学交流学习经验。',
    badges: ['APU学生', '计算机科学', '前端开发', 'React', 'TypeScript'],
    isOwnProfile: true
  };

  // 模拟用户的帖子数据
  const userPosts = [
    {
      id: '1',
      author: {
        name: userData.name,
        avatar: userData.avatar,
        badge: 'APU学生'
      },
      content: '今天完成了React项目的重构，使用了TypeScript和Tailwind CSS，代码质量提升了很多！\n\n#React #TypeScript #前端开发',
      image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop',
      likes: 45,
      comments: 8,
      timestamp: '1天前',
      isLiked: false,
      isBookmarked: false,
      tags: ['React', 'TypeScript', '前端开发']
    },
    {
      id: '2',
      author: {
        name: userData.name,
        avatar: userData.avatar,
        badge: 'APU学生'
      },
      content: '在APU的图书馆学习了一整天，环境真的很棒！推荐给所有需要安静学习环境的同学。',
      likes: 32,
      comments: 5,
      timestamp: '3天前',
      isLiked: true,
      isBookmarked: false,
      tags: ['APU学习', '图书馆']
    }
  ];

  const handleEditProfile = () => {
    console.log('Edit profile');
    // 这里会打开编辑资料的模态框或跳转到编辑页面
  };

  const handleFollow = () => {
    console.log('Follow user');
    // 这里会处理关注用户的逻辑
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

  const tabs = [
    { id: 'posts', label: '帖子', count: userPosts.length },
    { id: 'likes', label: '点赞', count: 128 },
    { id: 'bookmarks', label: '收藏', count: 42 },
    { id: 'following', label: '关注', count: 156 },
    { id: 'followers', label: '粉丝', count: 89 }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Profile Card */}
      <ProfileCard
        user={userData}
        onEdit={handleEditProfile}
        onFollow={handleFollow}
        className="mb-8"
      />

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{userPosts.length}</div>
            <div className="text-sm text-gray-600">帖子</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">128</div>
            <div className="text-sm text-gray-600">点赞</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">156</div>
            <div className="text-sm text-gray-600">关注</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">89</div>
            <div className="text-sm text-gray-600">粉丝</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex space-x-8 border-b">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
              <span className="ml-1 text-gray-500">({tab.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'posts' && (
          <>
            {userPosts.length > 0 ? (
              userPosts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onLike={handleLike}
                  onBookmark={handleBookmark}
                  onShare={handleShare}
                  onComment={handleComment}
                />
              ))
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="text-gray-500">
                    <p className="text-lg mb-2">还没有发布任何帖子</p>
                    <p className="text-sm">分享你的第一个想法吧！</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {activeTab === 'likes' && (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500">
                <p className="text-lg mb-2">点赞的帖子</p>
                <p className="text-sm">这里会显示你点赞过的帖子</p>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'bookmarks' && (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500">
                <p className="text-lg mb-2">收藏的帖子</p>
                <p className="text-sm">这里会显示你收藏的帖子</p>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'following' && (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500">
                <p className="text-lg mb-2">关注的用户</p>
                <p className="text-sm">这里会显示你关注的用户列表</p>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'followers' && (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500">
                <p className="text-lg mb-2">粉丝列表</p>
                <p className="text-sm">这里会显示你的粉丝列表</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Profile;
